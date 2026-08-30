from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.paper import PaperResponse, PaperCreate
from app.services import paper_service


router = APIRouter(
    prefix="/papers",
    tags=["Papers"]
)

@router.post("/", response_model=PaperResponse)
def create_paper(
    paper: PaperCreate,
    db: Session = Depends(get_db)
):

    return paper_service.create_paper(
        db,
        paper
    )


@router.get("/", response_model=List[PaperResponse])
def get_all_papers(
    db: Session = Depends(get_db)
):
    return paper_service.get_papers(db)

@router.get("/{paper_id}", response_model=PaperResponse)
def get_single_paper(
    paper_id: int,
    db: Session = Depends(get_db)
):

    paper = paper_service.get_paper(
        db,
        paper_id
    )

    if not paper:
        raise HTTPException(
            status_code=404,
            detail="Paper not found"
        )
    
    return paper


@router.get("/{paper_id}")
def delete_single_paper(
    paper_id: int,
    db: Session = Depends(get_db)
):

    deleted = paper_service.delete_paper(
        db,
        paper_id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Paper not found"
        )
    
    return {
        "message": "Paper deleted successfully"
    }



