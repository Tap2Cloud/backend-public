from celery import shared_task

from t2c_backend.clients.email_provider import Config


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def verification_mail(
    self,
    user_email: str,
    first_name: str,
    code: str,
    expiry_minutes: int,
    action_url: str,
    template_slug: str,
    project_id: int | None,
    from_name: str | None,
) -> None:
    correlation_id = self.request.id
    self.app.fast_app.clients.email_provider.send_email(
        to=[user_email],
        template_slug=template_slug,
        project_id=project_id,
        from_name=from_name,
        tags={
            "first_name": first_name,
            "user_email": user_email,
            "code": code,
            "expiry_minutes": str(expiry_minutes),
            "action_url": action_url,
        },
        metadata={"correlation_id": correlation_id},
        idempotency_key=correlation_id,
    )


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def forgot_password_mail(self, user_email: str, reset_password_link: str) -> None:
    self.app.fast_app.clients.email_provider.send_email(
        to=[user_email],
        template_slug=Config().RESET_PASSWORD_EMAIL_TEMPLATE_ID,
        tags={"reset_password_link": reset_password_link},
    )
