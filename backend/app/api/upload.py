from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.paper import Paper
from app.schemas.paper import PaperResponse
from app.services.pdf_service import save_pdf


router = APIRouter(
    prefix="/upload",
    tags=["Upload"],
)


@router.post(
    "/",
    response_model=PaperResponse,
)
async def upload_paper(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    # Validate file type
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed.",
        )

    # Validate filename
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required.",
        )

    # Save PDF
    file_path = await save_pdf(file)

    # Create database record
    paper = Paper(
        title=file.filename,
        file_path=file_path,
    )

    db.add(paper)
    db.commit()
    db.refresh(paper)

    return paper