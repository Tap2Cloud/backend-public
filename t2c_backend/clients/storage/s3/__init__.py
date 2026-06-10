from t2c_backend.clients.storage.interface import StorageInterface


class S3Storage(StorageInterface):
    def __init__(self, app, config):
        self.app = app
        self.config = config
