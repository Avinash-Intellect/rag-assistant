from config import CHUNK_SIZE, CHUNK_OVERLAP


def chunk_text(documents):
    """
    Splits page-level documents into smaller chunks.
    """

    chunks = []

    for doc in documents:
        text = doc["text"]
        metadata = doc["metadata"]

        start = 0
        chunk_count = 0

        while start < len(text):

            end = start + CHUNK_SIZE
            chunk_text = text[start:end]

            chunk_metadata = {
                **metadata,
                "chunk_id": f"{metadata['source']}_page{metadata['page']}_chunk{chunk_count}"
            }

            chunks.append({
                "text": chunk_text,
                "metadata": chunk_metadata
            })

            start += CHUNK_SIZE - CHUNK_OVERLAP
            chunk_count += 1

    return chunks
