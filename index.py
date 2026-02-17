from loader import load_documents
from chunker import chunk_text
from embedder import generate_embeddings
from vector_store import store_embeddings

print("Indexing documents...")

docs = load_documents("data")
chunks = chunk_text(docs)

embeddings = generate_embeddings(chunks)

store_embeddings(chunks, embeddings)

print("Indexing complete.")
