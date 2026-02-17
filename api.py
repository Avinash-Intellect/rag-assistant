from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import os

# Gemini config
from config import gemini_client, GEMINI_MODEL

# RAG components
from loader import load_documents
from chunker import chunk_text
from keyword_retriever import KeywordRetriever
from retriever import retrieve_context
from generator import generate_answer
from query_augmented import augment_query
from fastapi import UploadFile, File
from vector_store import store_embeddings
from embedder import generate_embeddings
from vector_store import collection_exists, sanitize_collection_name


# Session-based memory
from session_manager import SessionManager

# Cache and limiter
from cache import ResponseCache
from limiter import RateLimiter


# ==============================
# FastAPI Initialization
# ==============================

app = FastAPI(title="Placement RAG Assistant API")


# ==============================
# Request Schema
# ==============================

class QuestionRequest(BaseModel):

    question: str
    session_id: str
    pdf_name: str



# ==============================
# Initialize Global Components
# ==============================

print("Loading documents...")

docs = load_documents("data")
chunks = chunk_text(docs)

keyword_retriever = KeywordRetriever(chunks)

# Session manager (handles per-user memory)
session_manager = SessionManager()

# Cache responses for 1 hour
cache = ResponseCache(ttl=3600)

# Rate limiter
limiter = RateLimiter(max_calls=15, period=60)

print("System ready.")


# ==============================
# Standard Endpoint
# ==============================

@app.post("/ask")
def ask_question(request: QuestionRequest):

    question = request.question

    # Create or get session
    if request.session_id:
        session_id = request.session_id
    else:
        session_id = session_manager.create_session()

    memory = session_manager.get_memory(session_id)

    # Memory-aware query
    memory_context = memory.get_context()

    standalone_question = augment_query(question, memory_context)

    # Cache check
    cached_response = cache.get(standalone_question)

    if cached_response:
        print("Cache hit")

        return {
            "answer": cached_response["answer"],
            "sources": cached_response["sources"],
            "session_id": session_id
        }

    # Rate limiter check
    if not limiter.allow():

        return {
            "answer": "Rate limit exceeded. Please wait before making more requests.",
            "sources": [],
            "session_id": session_id
        }

    # Retrieve context
    result = retrieve_context(
    standalone_question,
    keyword_retriever,
    request.pdf_name
    )


    if result is None:

        return {
            "answer": "I could not find relevant information in the notes.",
            "sources": [],
            "session_id": session_id
        }

    context = result["context"]
    sources = result["sources"]

    # Generate answer
    answer = generate_answer(standalone_question, context)

    response_data = {
        "answer": answer,
        "sources": sources
    }

    # Store in cache
    cache.set(standalone_question, response_data)

    # Store in session memory
    memory.add(question, answer)

    return {
        "answer": answer,
        "sources": sources,
        "session_id": session_id
    }


# ==============================
# Streaming Endpoint
# ==============================

@app.post("/ask-stream")
def ask_question_stream(request: QuestionRequest):

    question = request.question

    # Create or get session
    if request.session_id:
        session_id = request.session_id
    else:
        session_id = session_manager.create_session()

    memory = session_manager.get_memory(session_id)

    memory_context = memory.get_context()

    standalone_question = augment_query(question, memory_context)

    # Cache check
    cached_response = cache.get(standalone_question)

    if cached_response:

        def cached_stream():
            yield cached_response["answer"]

        return StreamingResponse(cached_stream(), media_type="text/plain")

    # Rate limiter check
    if not limiter.allow():

        def limit_stream():
            yield "Rate limit exceeded. Please wait."

        return StreamingResponse(limit_stream(), media_type="text/plain")

    # Retrieve context
    result = retrieve_context(
    standalone_question,
    keyword_retriever,
    request.pdf_name
    )


    if result is None:

        def error_stream():
            yield "I could not find relevant information in the notes."

        return StreamingResponse(error_stream(), media_type="text/plain")

    context = result["context"]
    sources = result["sources"]

    # Streaming generator
    def stream_generator():

        prompt = f"""
You are a placement preparation assistant.

Answer strictly using the provided context.
Cite sources using [number].
Do NOT hallucinate.

Context:
{context}

Question:
{standalone_question}

Answer:
"""

        response = gemini_client.models.generate_content_stream(
            model=GEMINI_MODEL,
            contents=prompt
        )

        full_text = ""

        for chunk in response:
            if chunk.text:
                full_text += chunk.text
                yield chunk.text

        # Save in cache
        cache.set(standalone_question, {
            "answer": full_text,
            "sources": sources
        })

        # Save in session memory
        memory.add(question, full_text)

    return StreamingResponse(stream_generator(), media_type="text/plain")
@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):

    try:

        file_path = os.path.join("data", file.filename)

        # Save file if not exists
        if not os.path.exists(file_path):

            with open(file_path, "wb") as f:
                f.write(await file.read())

        collection_name = sanitize_collection_name(file.filename)

        # CRITICAL FIX: Check if already indexed
        if collection_exists(collection_name):

            return {
                "message": "PDF already indexed",
                "pdf_name": file.filename
            }

        # Index only if not indexed
        docs = load_documents(file_path)

        chunks = chunk_text(docs)

        embeddings = generate_embeddings(chunks)

        store_embeddings(chunks, embeddings, file.filename)

        return {
            "message": "PDF uploaded and indexed successfully",
            "pdf_name": file.filename
        }

    except Exception as e:

        return {
            "error": str(e)
        }

