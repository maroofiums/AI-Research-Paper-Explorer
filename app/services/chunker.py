"""
Splits full paper text into overlapping chunks using LangChain's
RecursiveCharacterTextSplitter, then adapts the output into our own
Chunk schema -- same adapter pattern as arxiv_loader.py, so LangChain's
internal text-splitting representation stays contained to this module.
"""

from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.models.schemas import Chunk


def chunk_text(text: str, paper_id: str, chunk_size: int, overlap: int) -> List[Chunk]:
    """
    Split `text` into a List of Chunk objects, each up to `chunk_size`
    characters long, with `overlap` characters repeated between
    consecutive chunks.
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    raw_chunks = splitter.split_text(text)

    return [
        Chunk(
            chunk_id=f"{paper_id}_{i}",
            paper_id=paper_id,
            chunk_index=i,
            text=chunk,
            word_count=len(chunk.split()),
        )
        for i, chunk in enumerate(raw_chunks)
    ]