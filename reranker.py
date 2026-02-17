from config import gemini_client, GEMINI_MODEL


def rerank_chunks(query, chunks, top_k=3):
    """
    Uses Gemini to rerank retrieved chunks based on relevance.
    Returns top_k most relevant chunks.
    """

    # Prepare chunk list for LLM
    chunk_descriptions = ""

    for i, chunk in enumerate(chunks, start=1):
        chunk_descriptions += f"""
Chunk {i}:
Source: {chunk['metadata']['source']}
Page: {chunk['metadata']['page']}
Content: {chunk['text']}
"""

    prompt = f"""
You are a semantic reranking system.

Your job is to rank document chunks by relevance to the user query.

Query:
{query}

Document Chunks:
{chunk_descriptions}

Instructions:
- Select the {top_k} most relevant chunks.
- Return ONLY their chunk numbers in order of relevance.
- Example output format: 3,1,5
"""

    response = gemini_client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt
    )

    ranking_text = response.text.strip()

    try:
        indices = [int(x.strip()) - 1 for x in ranking_text.split(",")]
        reranked_chunks = [chunks[i] for i in indices if i < len(chunks)]
    except:
        # fallback if parsing fails
        reranked_chunks = chunks[:top_k]

    return reranked_chunks[:top_k]
