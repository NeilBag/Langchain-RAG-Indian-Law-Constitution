import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    CHUNK_SIZE = 8000
    CHUNK_OVERLAP = 1000
    
    # Gemini model configuration
    GEMINI_MODEL = "gemini-2.0-flash-thinking-exp-01-21"
    EMBEDDING_MODEL = "models/embedding-001"
    
    # Vector DB settings
    COLLECTION_NAME = "indian_legal_docs"
    
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY environment variable is required")