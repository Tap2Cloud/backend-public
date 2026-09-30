from celery import current_app as current_celery_app

from t2c_backend.clients.celery_app.config import Config


class CeleryApp:
    def __init__(self, app) -> None:
        self.app = app
        self.celery = CeleryApp.create_celery(app)

    @staticmethod
    def create_celery(app):
        celery_app = current_celery_app
        celery_app.fast_app = app
        celery_app.config_from_object(Config(), namespace="CELERY")
        celery_app.conf.update(task_track_started=True)
        celery_app.conf.update(task_serializer="pickle")
        celery_app.conf.update(result_serializer="pickle")
        celery_app.conf.update(accept_content=["pickle", "json"])
        celery_app.conf.update(result_expires=200)
        celery_app.conf.update(result_persistent=True)
        celery_app.conf.update(worker_send_task_events=False)
        celery_app.conf.update(worker_prefetch_multiplier=1)
        celery_app.conf.update(broker_connection_retry_on_startup=True)

        celery_app.conf.timezone = "UTC"

        return celery_app


async def setup(app):
    return app.add_client(CeleryApp(app))
