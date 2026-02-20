import os
from dotenv import load_dotenv
from google import genai
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file")
gemini_client = genai.Client(api_key=GEMINI_API_KEY)
GEMINI_MODEL = "gemini-2.5-flash-lite"



EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE = 500        # characters per chunk
CHUNK_OVERLAP = 100     # overlap between chunks
CHROMA_DB_PATH = "db"
COLLECTION_NAME = "placement_notes"
SIMILARITY_THRESHOLD = 0.8

def get_gemini_model():
    from google import genai
    return genai.GenerativeModel(GEMINI_MODEL)
