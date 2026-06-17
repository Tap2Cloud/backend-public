from pydantic import BaseModel


class Pagination(BaseModel):
    page: int
    pagesize: int
