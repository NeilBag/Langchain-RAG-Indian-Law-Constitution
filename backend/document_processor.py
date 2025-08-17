import os
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain.schema import Document
from backend.config import Config

class DocumentProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )
    
    def load_pdf(self, file_path: str) -> List[Document]:
        """Load and process PDF documents"""
        try:
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            
            # Add metadata to identify document type
            doc_name = os.path.basename(file_path).lower()
            print(f"Processing file: {doc_name}")
            
            # Enhanced document type detection including Income Tax
            if "250883" in doc_name or "constitution" in doc_name:
                doc_type = "constitution"
                print(f"Detected as Constitution document: {doc_name}")
            elif "2023-45" in doc_name or "nyaya" in doc_name or "sanhita" in doc_name:
                doc_type = "nyaya_sanhita"
                print(f"Detected as Bharatiya Nyaya Sanhita document: {doc_name}")
            elif ("income-tax" in doc_name or "finance" in doc_name or 
                  "tax" in doc_name or "1961" in doc_name or "1962" in doc_name):
                doc_type = "income_tax"
                print(f"Detected as Income Tax document: {doc_name}")
            else:
                # Try to detect from content - check multiple pages
                sample_texts = []
                for i in range(min(3, len(documents))):  # Check first 3 pages
                    sample_texts.append(documents[i].page_content.lower())
                
                combined_text = " ".join(sample_texts)
                
                if ("income tax" in combined_text or 
                    "tax deduction" in combined_text or
                    "assessment" in combined_text or
                    "taxable income" in combined_text or
                    "finance act" in combined_text or
                    "central board of direct taxes" in combined_text):
                    doc_type = "income_tax"
                    print(f"Content-detected as Income Tax document: {doc_name}")
                elif ("bharatiya nyaya sanhita" in combined_text or 
                    "criminal law" in combined_text or 
                    "offence" in combined_text or
                    "punishment" in combined_text or
                    "section" in combined_text and "imprisonment" in combined_text):
                    doc_type = "nyaya_sanhita"
                    print(f"Content-detected as Bharatiya Nyaya Sanhita: {doc_name}")
                elif ("constitution of india" in combined_text or 
                      "fundamental rights" in combined_text or
                      "article" in combined_text and "parliament" in combined_text):
                    doc_type = "constitution"
                    print(f"Content-detected as Constitution: {doc_name}")
                else:
                    doc_type = "legal_document"
                    print(f"Detected as general legal document: {doc_name}")
            
            for i, doc in enumerate(documents):
                doc.metadata.update({
                    "source": file_path,
                    "document_type": doc_type,
                    "file_name": os.path.basename(file_path),
                    "page_number": i + 1,
                    "chunk_id": f"{os.path.basename(file_path)}_page_{i+1}"
                })
            
            return documents
        except Exception as e:
            print(f"Error loading PDF {file_path}: {str(e)}")
            return []
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into chunks"""
        chunks = self.text_splitter.split_documents(documents)
        
        # Add chunk-specific metadata
        for i, chunk in enumerate(chunks):
            chunk.metadata.update({
                "chunk_index": i,
                "content_preview": chunk.page_content[:100].replace('\n', ' ')
            })
        
        return chunks
    
    def process_documents(self, file_paths: List[str]) -> List[Document]:
        """Process multiple PDF files"""
        all_documents = []
        
        for file_path in file_paths:
            if os.path.exists(file_path) and file_path.endswith('.pdf'):
                documents = self.load_pdf(file_path)
                all_documents.extend(documents)
            else:
                print(f"File not found or not a PDF: {file_path}")
        
        # Split all documents into chunks
        chunked_documents = self.split_documents(all_documents)
        print(f"Processed {len(chunked_documents)} document chunks")
        
        return chunked_documents