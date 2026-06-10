from t2c_backend.clients.storage.config import Config
from t2c_backend.clients.storage.disk import DiskStorage
from t2c_backend.clients.storage.s3 import S3Storage


class Storage:
    def __init__(self, app) -> None:
        self.app = app

    @staticmethod
    def create(app):
        storage_config = Config()
        if storage_config.STORAGE_TYPE == "S3":
            return S3Storage(app, storage_config)
        elif storage_config.STORAGE_TYPE == "DISK":
            return DiskStorage(app, storage_config)
        else:
            raise ValueError(f"Unsupported storage type: {storage_config.STORAGE_TYPE}")


def setup(app):
    return app.add_client(Storage.create(app), "Storage")
