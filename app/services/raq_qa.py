"""
RAG ("chat with paper") answer generation: retrieves relevant chunks via
search.search_chunks, then asks an LLM to answer strictly from that
retrieved context. This grounding step is what makes it RAG rather than
just "ask an LLM and hope" -- the model only sees real, ingested paper
text, not its own (possibly wrong, possibly outdated) training memory.
"""

from dataclasses import dataclass
from functools import lru_cache

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_mistralai import ChatMistralAI

from app.config import settings
from app.services.search import ChunkResult, search_chunks

_SYSTEM_PROMPT = (
    "You are a research assistant answering questions strictly from the "
    "provided paper excerpts. Rules:\n"
    "1. Only use information present in the excerpts below -- do not use "
    "outside knowledge, even if you are confident it is correct.\n"
    "2. If the excerpts do not contain enough information to answer, say "
    "so explicitly rather than guessing.\n"
    "3. When you state a claim, reference which excerpt it came from, e.g. "
    "'(Excerpt 2)'."
)


@dataclass
class QAResult:
    answer: str
    sources: list[ChunkResult]


@lru_cache(maxsize=1)
def _get_llm() -> ChatMistralAI:
    if settings.mistral_api_key is None:
        raise RuntimeError(
            "MISTRAL_API_KEY is not set. Add it to your .env file to use "
            "the RAG question-answering endpoint -- ingestion and search "
            "don't need it."
        )
    return ChatMistralAI(
        model=settings.mistral_model,
        mistral_api_key=settings.mistral_api_key.get_secret_value(),
        temperature=0.1,
    )


def _build_context(chunks: list[ChunkResult]) -> str:
    """Number each chunk so the model (and the caller) can cite it precisely."""

    parts = [
        f"[Excerpt {i}] (from paper {c.chunk.paper_id})\n{c.chunk.text}"
        for i, c in enumerate(chunks, start=1)
    ]
    return "\n\n".join(parts)


def answer_question(
    question: str, paper_id: str | None = None, k: int = 5
) -> QAResult:
    """
    Answer a question grounded in retrieved chunks.

    `paper_id` scopes retrieval to one paper ("chat with this paper"); left
    as None, retrieval spans every ingested paper's chunks.
    """

    chunks = search_chunks(query=question, k=k, paper_id=paper_id)

    if not chunks:
        return QAResult(
            answer=(
                "No relevant content found in the ingested papers to "
                "answer this question."
            ),
            sources=[],
        )

    context = _build_context(chunks)
    llm = _get_llm()
    messages = [
        SystemMessage(content=_SYSTEM_PROMPT),
        HumanMessage(content=f"Excerpts:\n\n{context}\n\nQuestion: {question}"),
    ]
    response = llm.invoke(messages)

    return QAResult(answer=response.content, sources=chunks)