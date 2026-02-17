import chromadb
import re
from config import CHROMA_DB_PATH


client = chromadb.PersistentClient(path=CHROMA_DB_PATH)


def sanitize_collection_name(pdf_name):

    # remove .pdf
    name = pdf_name.replace(".pdf", "")

    # replace spaces with underscore
    name = name.replace(" ", "_")

    # remove invalid characters
    name = re.sub(r"[^a-zA-Z0-9._-]", "", name)

    # ensure starts and ends with alphanumeric
    name = name.strip("._-")

    return name


def get_collection(pdf_name):

    collection_name = sanitize_collection_name(pdf_name)

    collection = client.get_or_create_collection(
        name=collection_name
    )

    return collection




def collection_exists(collection_name):

    collections = client.list_collections()

    for collection in collections:
        if collection.name == collection_name:
            return True

    return False



def store_embeddings(chunks, embeddings, pdf_name):

    collection = get_collection(pdf_name)

    ids = [chunk["metadata"]["chunk_id"] for chunk in chunks]

    documents = [chunk["text"] for chunk in chunks]

    metadatas = [chunk["metadata"] for chunk in chunks]

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas
    )


def query_embeddings(query_embedding, pdf_name, top_k=5):

    collection = get_collection(pdf_name)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    return results
