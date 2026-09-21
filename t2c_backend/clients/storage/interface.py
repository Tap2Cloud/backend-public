import abc
import os.path
from collections.abc import AsyncGenerator

from fastapi import UploadFile

from t2c_backend.utils.enums import DocumentFor
from t2c_backend.utils.errors import BadRequestError


class StorageInterface(metaclass=abc.ABCMeta):
    @staticmethod
    def ensure_safe_filename(filename: str) -> str:
        """
        Refuse a filename that could address anything outside its own document directory.

        A filename reaches storage straight from the client - an upload carries its own,
        and a custom field's response_value is used as one - and is then joined onto the
        storage root. A name holding a path separator or a '..' would resolve to a file
        outside that root, so the join has to be given a bare name or nothing at all.
        """
        if not filename:
            raise BadRequestError("Document filename must not be empty")

        if (
            "\x00" in filename
            or "/" in filename
            or "\\" in filename
            or filename in (os.curdir, os.pardir)
        ):
            raise BadRequestError(f"Unsafe document filename: {filename!r}")

        return filename

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
