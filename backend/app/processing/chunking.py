from dataclasses import dataclass


@dataclass
class TextChunk:
    """A single chunk of text extracted from a document, ready for embedding."""

    content: str
    chunk_index: int
    start_char: int
    end_char: int


def chunk_text(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 150,
) -> list[TextChunk]:
    """Split text into overlapping chunks using a recursive-style separator strategy.

    Tries to split on paragraph breaks first, then sentences, then words,
    falling back to a hard character cut only if nothing else fits.
    """
    if not text or not text.strip():
        return []

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    separators = ["\n\n", "\n", ". ", " "]
    raw_chunks = _split_recursive(text, chunk_size, separators)

    return _apply_overlap_and_index(raw_chunks, text, chunk_overlap)


def _split_recursive(text: str, chunk_size: int, separators: list[str]) -> list[str]:
    """Recursively split text using the first separator that produces small-enough pieces."""
    if len(text) <= chunk_size:
        return [text] if text.strip() else []

    if not separators:
        # No separators left — hard cut at chunk_size.
        return [text[:chunk_size]] + _split_recursive(text[chunk_size:], chunk_size, separators)

    separator, *remaining_separators = separators
    pieces = text.split(separator)

    chunks: list[str] = []
    current = ""

    for piece in pieces:
        candidate = f"{current}{separator}{piece}" if current else piece

        if len(candidate) <= chunk_size:
            current = candidate
        else:
            if current:
                chunks.append(current)
            if len(piece) > chunk_size:
                chunks.extend(_split_recursive(piece, chunk_size, remaining_separators))
                current = ""
            else:
                current = piece

    if current:
        chunks.append(current)

    return chunks


def _apply_overlap_and_index(raw_chunks: list[str], original_text: str, chunk_overlap: int) -> list[TextChunk]:
    """Add character-based overlap between consecutive chunks and track positions."""
    result: list[TextChunk] = []
    search_start = 0

    for index, chunk in enumerate(raw_chunks):
        start_char = original_text.find(chunk, search_start)
        if start_char == -1:
            start_char = search_start

        end_char = start_char + len(chunk)
        search_start = max(start_char + 1, end_char - chunk_overlap)

        content = chunk
        if index > 0 and chunk_overlap > 0:
            overlap_start = max(0, start_char - chunk_overlap)
            overlap_text = original_text[overlap_start:start_char]
            content = overlap_text + chunk

        result.append(
            TextChunk(
                content=content.strip(),
                chunk_index=index,
                start_char=start_char,
                end_char=end_char,
            )
        )

    return [c for c in result if c.content]