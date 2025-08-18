import os
from backend.document_processor import DocumentProcessor
from backend.vector_store import VectorStore

# This script is intended to be run as a one-off task to index documents.

def initialize_documents():
    """Initializes the vector store with documents from the root and uploads folders."""

    # Get the absolute path of the directory where this script is located
    project_root = os.path.dirname(os.path.abspath(__file__))
    print(f"Searching for PDF documents in project root: {project_root}")

    document_processor = DocumentProcessor()
    vector_store = VectorStore()
    upload_folder = os.path.join(project_root, 'uploads')

    try:
        if vector_store.is_empty():
            print("Vector store is empty. Initializing with existing PDFs...")

            pdf_files = []

            # Check project root directory for PDF files
            for f in os.listdir(project_root):
                if f.lower().endswith('.pdf'):
                    pdf_files.append(os.path.join(project_root, f))

            # Check uploads directory for PDF files
            if os.path.exists(upload_folder):
                for f in os.listdir(upload_folder):
                    if f.lower().endswith('.pdf'):
                        pdf_files.append(os.path.join(upload_folder, f))

            if pdf_files:
                print(f"Found {len(pdf_files)} PDF files for indexing: {pdf_files}")
                documents = document_processor.process_documents(pdf_files)

                if documents:
                    vector_store.add_documents(documents)
                    print(f"Successfully indexed {len(documents)} document chunks from {len(pdf_files)} files.")
                else:
                    print("Could not process any documents from the PDF files.")
            else:
                print("No PDF files found to index.")
        else:
            print("Vector store is not empty. Skipping initialization.")

    except Exception as e:
        print(f"An error occurred during document initialization: {str(e)}")

if __name__ == "__main__":
    print("--- Starting document indexing process ---")
    initialize_documents()
    print("--- Document indexing process finished ---")
