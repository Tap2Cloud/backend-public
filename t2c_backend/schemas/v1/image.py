import base64

from fastapi import UploadFile
from pydantic import BaseModel


class Image(BaseModel):
    image: str
    filename: str
    content_type: str

    @staticmethod
    async def from_file(file: UploadFile) -> "Image":
        return Image(
            image=base64.b64encode(await file.read()).decode("ascii"),
            filename=file.filename,
            content_type=file.content_type,
        )

    def get_string(self) -> str:
        return f"data:{self.content_type};base64, {self.image}"
