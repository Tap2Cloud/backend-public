import os.path
import sys
from collections.abc import AsyncGenerator

import aiofiles
import aiofiles.os
from fastapi import UploadFile

from t2c_backend.clients.storage.interface import StorageInterface
from t2c_backend.utils.enums import DocumentFor


class DiskStorage(StorageInterface):
    def __init__(self, app, config):
        self.app = app
        self.config = config

    @staticmethod
    def add_unique_postfix(fn):
        if not os.path.exists(fn):
            return fn

        path, name = os.path.split(fn)
        name, ext = os.path.splitext(name)

        def make_fn(copy_number):
            return os.path.join(path, f"{name}({copy_number}){ext}")

        for i in range(2, sys.maxsize):
            uni_fn = make_fn(i)
            if not os.path.exists(uni_fn):
                return uni_fn

        return None

    async def save(
        self,
        save_path: str,
        file: UploadFile,
    ) -> UploadFile:
        root_path = os.path.join(str(self.app.config.project_root_path), self.config.BUCKET)
        final_file_path = os.path.join(root_path, save_path, file.filename)

        if os.path.exists(final_file_path):
            file.filename = self.add_unique_postfix(file.filename)
            final_file_path = os.path.join(root_path, save_path, file.filename)
        else:
            os.makedirs(os.path.join(root_path, save_path), exist_ok=True)

        async with aiofiles.open(final_file_path, "wb") as out_file:
            while content := await file.read(1024):
                await out_file.write(content)

        return file

    async def delete(
        self,
        file_path: str,
        filename: str,
    ) -> bool:
        root_path = os.path.join(str(self.app.config.project_root_path), self.config.BUCKET)
        final_file_path = os.path.join(root_path, file_path, filename)

        if not os.path.exists(final_file_path):
            return False

        await aiofiles.os.remove(final_file_path)

        parent_dir = os.path.dirname(final_file_path)
        if os.path.isdir(parent_dir) and not os.listdir(parent_dir):
            os.rmdir(parent_dir)

        return True

    async def get(self, final_file_path: str, chunk_size: int) -> AsyncGenerator[bytes, None]:
        async with aiofiles.open(final_file_path, mode="rb") as f:
            while content := await f.read(chunk_size):
                yield content

    async def save_document(
        self, organization_id: int, document_for: DocumentFor, file_id: int, file: UploadFile
    ) -> UploadFile:
        return await self.save(
            os.path.join(str(organization_id), str(document_for), str(file_id)),
            file,
        )

    async def delete_document(
        self, organization_id: int, document_for: DocumentFor, file_id: int, filename: str
    ) -> bool:
        return await self.delete(
            os.path.join(str(organization_id), str(document_for), str(file_id)),
            filename,
        )

    async def get_document(
        self,
        organization_id: int,
        document_for: DocumentFor,
        file_id: int,
        file_name: str,
        chunk_size: int = 4096,
    ) -> AsyncGenerator[bytes, None]:
        async for chunk in self.get(
            os.path.join(
                str(self.app.config.project_root_path),
                self.config.BUCKET,
                str(organization_id),
                str(document_for),
                str(file_id),
                file_name,
            ),
            chunk_size,
        ):
            yield chunk
