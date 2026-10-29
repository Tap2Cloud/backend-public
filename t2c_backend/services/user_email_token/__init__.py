import secrets
from uuid import uuid4

from t2c_backend.clients.celery_app.tasks import verification_mail
from t2c_backend.core.repository import BaseRepository
from t2c_backend.models import EmailTemplate, User, UserEmailToken
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

    async def send_verification_code(self, user: User) -> None:
        redis = self.app.clients.redis.client
        config = self.app.config
        await self._start_cooldown(user.email)
        template = await self.get_email_template(EmailTemplateType.verify_email, user.language)
        code = f"{secrets.randbelow(1_000_000):06d}"
        record = await self.create_token(user.id, TokenType.EmailVerificationToken)
        key = EMAIL_VERIFICATION_KEY.format(email=user.email)
        async with redis.pipeline(transaction=True) as pipe:
            pipe.delete(key)
            pipe.hset(key, mapping={"code": code, "attempts": 0})
            pipe.expire(key, config.USER_EMAIL_CODE_EXPIRY_MINUTES * 60)
            await pipe.execute()

        verification_page_url = (
            self.app.services.authentication.create_link_for_user_email_verification(
                record.user_token
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
            task_id=record.user_token,
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

    async def resend_verification_code(self, email: str) -> None:
        user = await self.app.services.user_service.repository.get_one_or_none(email=email)
        if not user:
            raise NotFoundError("Email not registered")

        if user.is_email_verified:
            raise AlreadyExistsError("Email already verified")

        await self.send_verification_code(user)

    async def verify_email_code(self, token: str, code: str) -> None:
        redis = self.app.clients.redis.client
        record = await self.find_by_token(token)
        if not record or record.type != TokenType.EmailVerificationToken:
            raise BadRequestError("Invalid or expired code")

        user = record.user
        if user.is_email_verified:
            raise AlreadyExistsError("Email already verified")
        is_newer_sent = await self.repository.exists(
            user_id=user.id, type=TokenType.EmailVerificationToken, id__gt=record.id
        )
        if is_newer_sent:
            raise BadRequestError("Invalid or expired code")

        key = EMAIL_VERIFICATION_KEY.format(email=user.email)
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

        await self.app.services.user_service.mark_email_verified(user)
        record.is_used = True
        await self.repository.save(record)

    async def _start_cooldown(self, email: str) -> None:
        redis = self.app.clients.redis.client
        cooldown_key = EMAIL_VERIFICATION_COOLDOWN_KEY.format(email=email)
        is_set = await redis.set(
            cooldown_key, 1, nx=True, ex=self.app.config.USER_EMAIL_CODE_RESEND_COOLDOWN_SECONDS
        )
        if not is_set:
            retry_after = await redis.ttl(cooldown_key)
            raise TooManyRequestsError(
                "Please wait before requesting a new code", retry_after=max(retry_after, 1)
            )

    def _is_token_expired(
        self,
        user_email_token: UserEmailToken,
        is_forgot_password: bool = False,
    ) -> bool:
        """Helper method to check if the token has expired."""
        expiry_hours = (
            self.app.config.USER_FORGOT_PASSWORD_TOKEN_EXPIRY_HOURS
            if is_forgot_password
            else self.app.config.USER_EMAIL_TOKEN_EXPIRY_HOURS
        )

        difference = aware_utcnow() - user_email_token.time
        hours = difference.total_seconds() / 3600
        return hours > expiry_hours

    async def verify_forgot_password_token_wrapper(self, token: UserEmailToken) -> str | bool:
        """Verifies the forgot password token."""

        if not token or token.type == TokenType.EmailVerificationToken:
            return "invalid token"

        if token.is_used:
            return "already verified"

        if self._is_token_expired(token, is_forgot_password=True):
            return "time expired"

        return True

    async def mark_forgot_password_token(self, token: str) -> str | int:
        user_email_token = await self.find_by_token(token)
        is_valid_token = await self.verify_forgot_password_token_wrapper(token=user_email_token)

        if is_valid_token is True:
            user_email_token.is_used = True
            await self.repository.save(user_email_token)
            return user_email_token.user_id

        return is_valid_token

    async def verify_forgot_password_token(self, token: str) -> str | bool:
        """Verifies the forgot password token."""

        user_email_token = await self.find_by_token(token)
        return await self.verify_forgot_password_token_wrapper(user_email_token)


def setup(app, session, *args, **kwargs):
    return app.add_service(UserEmailTokenService(app, session), session.info["session_id"])
