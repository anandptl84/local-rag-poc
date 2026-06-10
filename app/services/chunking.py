def chunk_text(text: str, size: int = 800, overlap: int = 150) -> list[str]:
    """Split text into word-aware overlapping chunks.

    Never splits mid-word. Each chunk is approximately `size` characters,
    with `overlap` characters of trailing words carried into the next chunk.
    """
    words = text.split()
    if not words:
        return []

    chunks: list[str] = []
    i = 0
    n = len(words)
    while i < n:
        current: list[str] = []
        current_len = 0
        j = i
        while j < n:
            w = words[j]
            added = len(w) + (1 if current else 0)
            if current and current_len + added > size:
                break
            current.append(w)
            current_len += added
            j += 1
        chunks.append(" ".join(current))
        if j >= n:
            break

        back_len = 0
        new_i = j
        while new_i > i + 1 and back_len < overlap:
            new_i -= 1
            back_len += len(words[new_i]) + 1
        i = new_i

    return chunks
