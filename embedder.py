from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL_NAME


# Load embedding model once (important for performance)
embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)


def generate_embeddings(chunks):
    """
    Generates embeddings for each chunk.
    """

    texts = [chunk["text"] for chunk in chunks]

    embeddings = embedding_model.encode(texts)

    return embeddings
