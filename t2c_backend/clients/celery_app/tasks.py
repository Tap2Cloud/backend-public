from celery import shared_task

from t2c_backend.clients.email_provider import Config


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 5},
)
def verification_mail(self, user_email: str, verification_link: str) -> None:
    self.app.fast_app.clients.email_provider.send_email(
        to=[user_email],
        template_slug=Config().VERIFICATION_EMAIL_TEMPLATE_ID,
        tags={"verification_link": verification_link},
    )


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 5},
)
def forgot_password_mail(self, user_email: str, reset_password_link: str) -> None:
    self.app.fast_app.clients.email_provider.send_email(
        to=[user_email],
        template_slug=Config().RESET_PASSWORD_EMAIL_TEMPLATE_ID,
        tags={"reset_password_link": reset_password_link},
    )
