import os
import uuid
from pathlib import Path

from fastapi import UploadFile


UPLOAD_DIR = Path("uploads/papers")


def create_upload_directory():
    """
    Create upload directory if it does not exist.
    """
    UPLOAD_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


async def save_pdf(
    file: UploadFile
) -> str:
    """
    Save uploaded PDF file and return file path.
    """

    create_upload_directory()

    file_extension = Path(
        file.filename
    ).suffix

    unique_filename = (
        f"{uuid.uuid4()}{file_extension}"
    )

    file_path = UPLOAD_DIR / unique_filename

    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    return str(file_path)