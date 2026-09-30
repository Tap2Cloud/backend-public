import lettr

from t2c_backend.clients.email_provider.config import Config


class EmailProvider:
    def __init__(self, app) -> None:
        self.app = app
        self.client = EmailProvider.get_client(app)

    @staticmethod
    def get_client(app):
        email_provider = lettr.Lettr(Config().EMAIL_PROVIDER_API_KEY)
        email_provider.auth_check()

        return email_provider

    def send_email(self, to: list, template_slug: str, tags: dict):
        return self.client.emails.send(
            from_email=Config().SENDER_EMAIL,
            to=to,
            template_slug=template_slug,
            substitution_data=tags,
        )


async def setup(app):
    return app.add_client(EmailProvider(app))
