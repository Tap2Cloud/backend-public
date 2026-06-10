import sqlalchemy

from t2c_backend.schemas.v1.image import Image


class ImageType(sqlalchemy.types.TypeDecorator):
    impl = sqlalchemy.types.JSON

    def process_bind_param(self, value, dialect):
        return value.model_dump() if value else None

    def process_result_value(self, value, dialect):
        return Image.model_validate(value) if value else None
