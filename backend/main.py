from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os
import shutil
from document_processor import DocumentProcessor
from vector_store import VectorStore
from rag_chain import RAGChain

app = FastAPI(title="Indian Legal RAG Chatbot", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
document_processor = DocumentProcessor()
vector_store = VectorStore()
rag_chain = RAGChain()

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]

@app.get("/")
async def root():
    return {"message": "Indian Legal RAG Chatbot API"}

@app.post("/upload-documents")
async def upload_documents(files: List[UploadFile] = File(...)):
    """Upload and process PDF documents"""
    try:
        uploaded_files = []
        
        # Create uploads directory if it doesn't exist
        os.makedirs("uploads", exist_ok=True)
        
        # Save uploaded files
        for file in files:
            if not file.filename.endswith('.pdf'):
                raise HTTPException(status_code=400, detail=f"Only PDF files are allowed. {file.filename} is not a PDF.")
            
            file_path = f"uploads/{file.filename}"
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            uploaded_files.append(file_path)
        
        # Process documents
        documents = document_processor.process_documents(uploaded_files)
        
        if not documents:
            raise HTTPException(status_code=400, detail="No documents could be processed")
        
        # Add to vector store
        vector_store.add_documents(documents)
        
        return {
            "message": f"Successfully processed {len(documents)} document chunks from {len(uploaded_files)} files",
            "files_processed": [os.path.basename(f) for f in uploaded_files]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing documents: {str(e)}")

@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """Query the RAG system"""
    try:
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        result = rag_chain.query(request.question)
        return QueryResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.post("/initialize-with-existing-pdfs")
async def initialize_with_existing_pdfs():
    """Initialize the system with PDFs in the current directory"""
    try:
        # Find PDF files in current directory
        pdf_files = [f for f in os.listdir(".") if f.endswith('.pdf')]
        
        if not pdf_files:
            return {"message": "No PDF files found in current directory"}
        
        # Process the PDF files
        documents = document_processor.process_documents(pdf_files)
        
        if not documents:
            raise HTTPException(status_code=400, detail="No documents could be processed")
        
        # Add to vector store
        vector_store.add_documents(documents)
        
        return {
            "message": f"Successfully initialized with {len(documents)} document chunks from {len(pdf_files)} files",
            "files_processed": pdf_files
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error initializing system: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)