import abc
from collections.abc import AsyncGenerator

from fastapi import UploadFile

from t2c_backend.utils.enums import DocumentFor


class StorageInterface(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    async def save(
        self,
        final_path: str,
        file: UploadFile,
    ) -> UploadFile:
        raise NotImplementedError

    @abc.abstractmethod
    async def delete(self, final_path: str, filename: str) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    async def get(self, final_file_path: str, chunk_size: int) -> AsyncGenerator[bytes, None]:
        raise NotImplementedError

    @abc.abstractmethod
    async def save_document(
        self,
        organization_id: int,
        document_for: DocumentFor,
        file_id: int,
        file: UploadFile,
    ) -> UploadFile:
        raise NotImplementedError

    @abc.abstractmethod
    async def delete_document(
        self,
        organization_id: int,
        document_for: DocumentFor,
        file_id: int,
        filename: str,
    ) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_document(
        self,
        organization_id: int,
        document_for: DocumentFor,
        file_id: int,
        file_name: str,
        chunk_size: int,
    ) -> AsyncGenerator[bytes, None]:
        raise NotImplementedError
