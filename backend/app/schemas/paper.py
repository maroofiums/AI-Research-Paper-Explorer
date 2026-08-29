from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PaperBase(BaseModel):
    title: str
    authors: str | None = None
    abstract: str | None = None


class PaperCreate(PaperBase):
    file_path: str


class PaperResponse(PaperBase):
    id: int
    file_path: str
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)