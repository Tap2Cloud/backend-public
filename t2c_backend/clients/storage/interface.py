import abc
from collections.abc import AsyncGenerator

from fastapi import UploadFile


class StorageInterface(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    async def save(
        self,
        final_path: str,
        file: UploadFile,
    ) -> UploadFile:
        raise NotImplementedError

    @abc.abstractmethod
    async def get(self, final_file_path: str, chunk_size: int) -> AsyncGenerator[bytes, None]:
        raise NotImplementedError

    @abc.abstractmethod
    async def save_audit_task_document(
        self,
        organization_id: int,
        task_id: int,
        file: UploadFile,
    ) -> UploadFile:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_audit_task_document(
        self, organization_id: int, task_id: int, file_name: str, chunk_size: int
    ) -> AsyncGenerator[bytes, None]:
        raise NotImplementedError
