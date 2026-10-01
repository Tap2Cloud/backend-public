import logging

import lettr

from t2c_backend.clients.email_provider.config import Config
from t2c_backend.utils.errors import EmailProviderError

logger = logging.getLogger(__name__)

# Temporary failures that are worth retrying (429, 5xx)
RETRYABLE_ERRORS = (lettr.RateLimitError, lettr.ServerError)


class EmailProvider:
    def __init__(self, app) -> None:
        self.app = app
        self.client = EmailProvider.get_client(app)

    @staticmethod
    def get_client(app):
        email_provider = lettr.Lettr(Config().EMAIL_PROVIDER_API_KEY)
        email_provider.auth_check()

        return email_provider

    @staticmethod
    def attachments(name: str, attachment_type: str, content):
        return lettr.Attachment(name, attachment_type, content)

    def send_email(self, to: list, template_slug: str, tags: dict, attachments: list = None):
        try:
            return self.client.emails.send(
                from_email=Config().SENDER_EMAIL,
                to=to,
                template_slug=template_slug,
                substitution_data=tags,
                attachments=attachments,
            )
        except lettr.LettrError as e:
            # ValidationError carries field errors, BadRequestError carries error_code
            details = getattr(e, "errors", None) or getattr(e, "error_code", None)
            logger.error(
                "Email send failed [%s]: %s %s", type(e).__name__, e.message, details or ""
            )
            raise EmailProviderError(e.message, retryable=isinstance(e, RETRYABLE_ERRORS)) from e


async def setup(app):
    return app.add_client(EmailProvider(app))
