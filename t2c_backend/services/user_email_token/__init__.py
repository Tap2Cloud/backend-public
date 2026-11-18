import secrets
from uuid import uuid4

from t2c_backend.clients.celery_app.tasks import (
    forgot_password_mail,
    verification_mail,
    welcome_mail,
)
from t2c_backend.core.repository import BaseRepository
from t2c_backend.models import EmailTemplate, Organization, User, UserEmailToken
from t2c_backend.utils.enums import EmailTemplateType, Language, TokenType
from t2c_backend.utils.errors import (
    AlreadyExistsError,
    BadRequestError,
    EmailProviderError,
    NotFoundError,
    TooManyRequestsError,
)
from t2c_backend.utils.misc import aware_utcnow

EMAIL_VERIFICATION_KEY = "email_verification:{email}"
EMAIL_VERIFICATION_COOLDOWN_KEY = "email_verification_cooldown:{email}"
FORGOT_PASSWORD_KEY = "forgot_password:{email}"
FORGOT_PASSWORD_COOLDOWN_KEY = "forgot_password_cooldown:{email}"


class UserEmailTokenService:
    _model = UserEmailToken

    def __init__(self, app, session) -> None:
        self.app = app
        self.repository = BaseRepository(app, session, self._model)
        self.email_template_repository = BaseRepository(app, session, EmailTemplate)

    async def create_token(self, user_id: int, token_type: TokenType) -> UserEmailToken:
        """Creates and saves a new email token."""
        user_email_token = UserEmailToken(user_id=user_id, user_token=uuid4().hex, type=token_type)
        return await self.repository.save(user_email_token, refresh=True)

    async def find_by_token(self, token: str) -> UserEmailToken | None:
        """Finds a user token by its string value."""
        return await self.repository.get_one_or_none(user_token=token, is_used__is_not=True)

    async def send_verification_code(self, user: User, frontend_url: str) -> None:
        config = self.app.config
        await self._start_cooldown(EMAIL_VERIFICATION_COOLDOWN_KEY.format(email=user.email))
        template = await self.get_email_template(EmailTemplateType.verify_email, user.language)
        record = await self._get_or_create_token(user, TokenType.EmailVerificationToken)
        code = await self._store_code(EMAIL_VERIFICATION_KEY.format(email=user.email))

        verification_page_url = (
            self.app.services.authentication.create_link_for_user_email_verification(
                record.user_token, frontend_url
            )
        )
        verification_mail.apply_async(
            kwargs={
                "user_email": user.email,
                "first_name": user.first_name,
                "code": code,
                "expiry_minutes": config.USER_EMAIL_CODE_EXPIRY_MINUTES,
                "action_url": verification_page_url,
                "template_slug": template.template_slug,
                "project_id": template.project_id,
                "from_name": template.from_name,
            },
        )

    async def send_welcome_mail(
        self, user: User, organization: Organization, frontend_url: str
    ) -> None:
        template = await self.get_email_template(EmailTemplateType.welcome, user.language)
        welcome_mail.apply_async(
            kwargs={
                "user_email": user.email,
                "first_name": user.first_name,
                "company_name": organization.name,
                "action_url": self.app.services.authentication.create_link_for_dashboard(
                    frontend_url
                ),
                "template_slug": template.template_slug,
                "project_id": template.project_id,
                "from_name": template.from_name,
            },
        )

    async def get_email_template(
        self, template_type: EmailTemplateType, language: Language
    ) -> EmailTemplate:
        environment = self.app.config.ENVIRONMENT
        template = await self.email_template_repository.get_one_or_none(
            type=template_type, language=language, environment=environment
        )
        if not template and language != Language.en:
            template = await self.email_template_repository.get_one_or_none(
                type=template_type, language=Language.en, environment=environment
            )
        if not template:
            raise EmailProviderError(f"No '{template_type}' email template for '{environment}'")
        return template

    async def resend_verification_code(
        self, email: str | None, token: str | None, frontend_url: str
    ) -> None:
        if email:
            user = await self.app.services.user_service.repository.get_one_or_none(email=email)
            if not user:
                raise NotFoundError("Email not registered")
        else:
            record = await self.repository.get_one_or_none(
                user_token=token, type=TokenType.EmailVerificationToken
            )
            if not record:
                raise BadRequestError("Invalid verification link")
            user = record.user

        if user.is_email_verified:
            raise AlreadyExistsError("Email already verified")

        await self.send_verification_code(user, frontend_url)

    async def verify_email_code(self, token: str, code: str) -> None:
        record = await self.find_by_token(token)
        if not record or record.type != TokenType.EmailVerificationToken:
            raise BadRequestError("Invalid or expired code")

        user = record.user
        if user.is_email_verified:
            raise AlreadyExistsError("Email already verified")

        await self._check_code(EMAIL_VERIFICATION_KEY.format(email=user.email), code)

        await self.app.services.user_service.mark_email_verified(user)
        record.is_used = True
        await self.repository.save(record)

    async def send_forgot_password_code(self, email: str) -> None:
        await self._start_cooldown(FORGOT_PASSWORD_COOLDOWN_KEY.format(email=email))
        user = await self.app.services.user_service.repository.get_one_or_none(email=email)
        if not user:
            return

        config = self.app.config
        template = await self.get_email_template(EmailTemplateType.forgot_password, user.language)
        code = await self._store_code(FORGOT_PASSWORD_KEY.format(email=user.email))
        forgot_password_mail.apply_async(
            kwargs={
                "user_email": user.email,
                "first_name": user.first_name,
                "code": code,
                "expiry_minutes": config.USER_EMAIL_CODE_EXPIRY_MINUTES,
                "template_slug": template.template_slug,
                "project_id": template.project_id,
                "from_name": template.from_name,
            },
        )

    async def verify_forgot_password_code(self, email: str, code: str) -> str:
        await self._check_code(FORGOT_PASSWORD_KEY.format(email=email), code)

        user = await self.app.services.user_service.repository.get_one_or_none(email=email)
        if not user:
            raise BadRequestError("Invalid or expired code")

        record = await self._get_or_create_token(user, TokenType.ForgotPasswordToken)
        return record.user_token

    async def reset_password(self, reset_token: str, password: str) -> None:
        record = await self.repository.get_one_or_none(
            user_token=reset_token, type=TokenType.ForgotPasswordToken, is_used__is_not=True
        )
        if not record or self._is_token_expired(record):
            raise BadRequestError("Invalid or expired reset token")

        await self.app.services.user_service.reset_password(
            user_id=record.user_id, password=password
        )
        record.is_used = True
        await self.repository.save(record)

    async def _get_or_create_token(self, user: User, token_type: TokenType) -> UserEmailToken:
        token = await self.repository.get_one_or_none(
            user_id=user.id, type=token_type, is_used__is_not=True
        )
        if not token:
            return await self.create_token(user.id, token_type)

        if token_type == TokenType.ForgotPasswordToken and self._is_token_expired(token):
            token.user_token = uuid4().hex
            token.time = aware_utcnow()
            token = await self.repository.save(token)
        return token

    async def _store_code(self, key: str) -> str:
        redis = self.app.clients.redis.client
        code = f"{secrets.randbelow(1_000_000):06d}"
        async with redis.pipeline(transaction=True) as pipe:
            pipe.delete(key)
            pipe.hset(key, mapping={"code": code, "attempts": 0})
            pipe.expire(key, self.app.config.USER_EMAIL_CODE_EXPIRY_MINUTES * 60)
            await pipe.execute()
        return code

    async def _check_code(self, key: str, code: str) -> None:
        redis = self.app.clients.redis.client
        async with redis.pipeline(transaction=True) as pipe:
            pipe.hincrby(key, "attempts", 1)
            pipe.hget(key, "code")
            attempts, stored_code = await pipe.execute()

        if stored_code is None:
            await redis.delete(key)
            raise BadRequestError("Invalid or expired code")

        if attempts > self.app.config.USER_EMAIL_CODE_MAX_ATTEMPTS:
            await redis.delete(key)
            raise TooManyRequestsError("Too many attempts, please request a new code")

        if not secrets.compare_digest(stored_code, code):
            raise BadRequestError("Invalid or expired code")

        await redis.delete(key)

    async def _start_cooldown(self, cooldown_key: str) -> None:
        redis = self.app.clients.redis.client
        is_set = await redis.set(
            cooldown_key, 1, nx=True, ex=self.app.config.USER_EMAIL_CODE_RESEND_COOLDOWN_SECONDS
        )
        if not is_set:
            retry_after = await redis.ttl(cooldown_key)
            raise TooManyRequestsError(
                "Please wait before requesting a new code", retry_after=max(retry_after, 1)
            )

    def _is_token_expired(self, user_email_token: UserEmailToken) -> bool:
        difference = aware_utcnow() - user_email_token.time
        hours = difference.total_seconds() / 3600
        return hours > self.app.config.USER_FORGOT_PASSWORD_TOKEN_EXPIRY_HOURS


def setup(app, session, *args, **kwargs):
    return app.add_service(UserEmailTokenService(app, session), session.info["session_id"])
