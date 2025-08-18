import chromadb
from typing import List
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.schema import Document
from backend.config import Config
from chromadb.config import Settings

class VectorStore:
    def __init__(self):
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=Config.EMBEDDING_MODEL,
            google_api_key=Config.GOOGLE_API_KEY
        )
        self.vector_store = None
        self.setup_vector_store()
    
    def is_empty(self) -> bool:
        """Check if vector store is empty"""
        try:
            # A more reliable way to check for emptiness is to get the item count.
            return self.vector_store._collection.count() == 0
        except Exception as e:
            print(f"Could not get collection count, assuming it's empty. Error: {e}")
            return True
    
    def setup_vector_store(self):
        """Initialize ChromaDB vector store"""
        try:
            self.vector_store = Chroma(
                collection_name=Config.COLLECTION_NAME,
                embedding_function=self.embeddings,
                persist_directory=Config.CHROMA_DB_PATH,
                client_settings=Settings(anonymized_telemetry=False)
            )
            print("Vector store initialized successfully")
        except Exception as e:
            print(f"Error initializing vector store: {str(e)}")
            raise
    
    def add_documents(self, documents: List[Document]):
        """Add documents to vector store"""
        try:
            if not documents:
                print("No documents to add")
                return
            
            # Add documents to vector store
            self.vector_store.add_documents(documents)
            
            # Persist the vector store
            self.vector_store.persist()
            print(f"Added {len(documents)} documents to vector store")
            
        except Exception as e:
            print(f"Error adding documents to vector store: {str(e)}")
            raise
    
    def similarity_search(self, query: str, k: int = 8) -> List[Document]:
        """Search for similar documents with enhanced retrieval"""
        try:
            # Use MMR for diverse results
            results = self.vector_store.max_marginal_relevance_search(
                query, 
                k=k, 
                fetch_k=k*3,  # Fetch more candidates
                lambda_mult=0.6  # Balance relevance vs diversity
            )
            return results
        except Exception as e:
            print(f"Error during similarity search: {str(e)}")
            # Fallback to regular similarity search
            try:
                results = self.vector_store.similarity_search(query, k=k)
                return results
            except:
                return []
    
    def similarity_search_with_score(self, query: str, k: int = 8) -> List[tuple]:
        """Search for similar documents with relevance scores"""
        try:
            results = self.vector_store.similarity_search_with_score(query, k=k)
            return results
        except Exception as e:
            print(f"Error during similarity search with score: {str(e)}")
            return []
    
    def get_retriever(self, k: int = 12):
        """Get retriever for RAG chain with diverse results"""
        return self.vector_store.as_retriever(
            search_type="mmr",  # Maximum Marginal Relevance for diversity
            search_kwargs={
                "k": k,
                "fetch_k": k * 2,  # Fetch more candidates for diversity
                "lambda_mult": 0.7  # Balance between relevance and diversity
            }
        )