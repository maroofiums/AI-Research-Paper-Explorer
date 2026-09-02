"""
Splits full paper text into overlapping chunks, sized by word count.

We deliberately avoid a network-dependent tokenizer (e.g. tiktoken, which
downloads its BPE ranks file from OpenAI's blob storage on first use) for
something as simple as length-bounding a chunk. Word count is a reasonable
proxy for token count in English text (~1 word ≈ 1.3 tokens) and keeps this
module fully offline after `pip install`.

Overlap between consecutive chunks preserves context across chunk
boundaries, which matters once these chunks are embedded and retrieved for
RAG (Phase 4): without overlap, a sentence split across two chunks can lose
meaning in both.

Note: once Phase 2 loads the actual chunk-embedding model
(sentence-transformers/all-MiniLM-L6-v2), chunk sizing could be refined to
respect that model's real tokenizer and max sequence length. Word-count
chunking is a deliberately simple placeholder until then.
"""

from app.models.schemas import Chunk


def chunk_text(text: str, paper_id: str, chunk_size: int, overlap: int) -> list[Chunk]:
    """
    Split `text` into a list of Chunk objects, each roughly `chunk_size`
    words long, with `overlap` words repeated between consecutive chunks.
    """

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    words = text.split()
    stride = chunk_size - overlap

    chunks: list[Chunk] = []
    chunk_index = 0
    for start in range(0, len(words), stride):
        window = words[start : start + chunk_size]
        if not window:
            break

        chunks.append(
            Chunk(
                chunk_id=f"{paper_id}_{chunk_index}",
                paper_id=paper_id,
                chunk_index=chunk_index,
                text=" ".join(window),
                word_count=len(window),
            )
        )
        chunk_index += 1

        # Stop once this window reached the end of the word sequence.
        if start + chunk_size >= len(words):
            break

    return chunks
