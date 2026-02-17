from embedder import embedding_model
from vector_store import query_embeddings
from config import SIMILARITY_THRESHOLD
from query_rewriter import rewrite_query


def retrieve_context(question, keyword_retriever, pdf_name, top_k=5):

    # Step 1: Encode query
    query_embedding = embedding_model.encode(question)

    # Step 2: Query vector DB using correct collection
    vector_results = query_embeddings(
        query_embedding,
        pdf_name,
        top_k=top_k
    )

    # Step 3: Safety check
    if (
        not vector_results
        or "documents" not in vector_results
        or not vector_results["documents"]
        or not vector_results["documents"][0]
    ):
        return None

    vector_docs = vector_results["documents"][0]
    vector_meta = vector_results["metadatas"][0]
    vector_dist = vector_results["distances"][0]

    # Step 4: Similarity threshold check
    if not vector_dist or vector_dist[0] > SIMILARITY_THRESHOLD:

        # OPTIONAL query rewrite (disable if quota issue)
        try:
            refined_query = rewrite_query(question)
        except Exception:
            refined_query = question

        # Re-embed rewritten query
        query_embedding = embedding_model.encode(refined_query)

        vector_results = query_embeddings(
            query_embedding,
            pdf_name,
            top_k=top_k
        )

        if (
            not vector_results
            or not vector_results["documents"]
            or not vector_results["documents"][0]
        ):
            return None

        vector_docs = vector_results["documents"][0]
        vector_meta = vector_results["metadatas"][0]
        vector_dist = vector_results["distances"][0]

        if not vector_dist or vector_dist[0] > SIMILARITY_THRESHOLD:
            return None

    # Step 5: Merge keyword + vector retrieval
    merged = {}

    # Vector results first (higher priority)
    for doc, meta in zip(vector_docs, vector_meta):
        merged[meta["chunk_id"]] = {
            "text": doc[:400],   # limit text length

            "metadata": meta
        }

    # Keyword results
    try:
        keyword_chunks = keyword_retriever.retrieve(question, top_k=top_k)

        for chunk in keyword_chunks:
            cid = chunk["metadata"]["chunk_id"]
            if cid not in merged:
                merged[cid] = chunk

    except Exception:
        pass

    # Step 6: Limit results
    MAX_CHUNKS = 3   # reduce from 5 to 3
    final_chunks = list(merged.values())[:MAX_CHUNKS]


    if not final_chunks:
        return None

    # Step 7: Build context and sources
    context_list = []
    sources = []

    for idx, chunk in enumerate(final_chunks, start=1):

        meta = chunk["metadata"]

        context_list.append(
            f"""
Source [{idx}]: {meta['source']}
Page [{idx}]: {meta['page']}
Content [{idx}]: {chunk['text']}
"""
        )

        sources.append({
            "index": idx,
            "source": meta["source"],
            "page": meta["page"]
        })

    context = "\n\n".join(context_list)

    return {
        "context": context,
        "sources": sources
    }
