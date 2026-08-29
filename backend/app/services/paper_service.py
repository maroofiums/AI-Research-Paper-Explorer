from sqlalchemy.orm import Session
from typing import List

from app.models.paper import Paper
from app.schemas.paper import PaperCreate


def create_paper(
    db: Session,
    paper_data: PaperCreate
) -> Paper:

    new_paper = Paper(
        title=paper_data.title,
        authors=paper_data.authors,
        abstract=paper_data.abstract,
        file_path=paper_data.file_path,
    )

    db.add(new_paper)
    db.commit()
    db.refresh(new_paper)

    return new_paper


def get_papers(
    db: Session
) -> List[Paper]:

    return db.query(Paper).all()


def get_paper(
    db: Session,
    paper_id: int
) -> Paper | None:

    return (
        db.query(Paper)
        .filter(Paper.id == paper_id)
        .first()
    )


def delete_paper(
    db: Session,
    paper_id: int
) -> bool:

    paper = get_paper(db, paper_id)

    if not paper:
        return False

    db.delete(paper)
    db.commit()

    return True