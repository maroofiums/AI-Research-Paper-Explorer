"""
POST /qa/ask

Exposes the RAG "chat with paper" pipeline in services/rag_qa.py over
HTTP. A POST, not GET like /search: unlike a search query, a question can
be long free text, and this call has a real cost (a paid Mistral API
call) -- that fits a POST body better than query parameters, which are
better suited to cheap, cacheable, side-effect-free reads.
"""

import asyncio

from fastapi import APIRouter, HTTPException

from app.models.schemas import ChunkSearchResult, QARequest, QAResponse
from app.services import rag_qa

router = APIRouter(prefix="/qa", tags=["qa"])


@router.post("/ask", response_model=QAResponse)
async def ask(request: QARequest) -> QAResponse:
    try:
        result = await asyncio.to_thread(
            rag_qa.answer_question, request.question, request.paper_id, request.k
        )
    except RuntimeError as exc:
        # Raised by rag_qa._get_llm() when MISTRAL_API_KEY isn't configured --
        # translate it into a clear HTTP response instead of a bare 500.
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return QAResponse(
        answer=result.answer,
        sources=[
            ChunkSearchResult(chunk=r.chunk, score=r.score) for r in result.sources
        ],
    )