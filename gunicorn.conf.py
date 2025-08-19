# Gunicorn configuration file

# Worker settings
workers = 4  # Number of worker processes
worker_class = "gevent"  # Asynchronous worker
timeout = 120  # Worker timeout in seconds

# Server hooks
def on_starting(server):
    """
    This hook is called when the master process is starting.
    We will use it to initialize the vector store once, before
    any worker processes are forked.
    """
    print("GUNICORN: Master process is starting. Initializing vector store...")

    import os
    from backend.document_processor import DocumentProcessor
    from backend.vector_store import VectorStore

    # Initialize components
    document_processor = DocumentProcessor()
    vector_store = VectorStore()

    if vector_store.is_empty():
        print("GUNICORN: Vector store is empty. Starting initialization.")

        project_root = os.path.dirname(os.path.abspath(__file__))
        upload_folder = os.path.join(project_root, 'uploads')

        pdf_files = []

        # Find PDFs in project root
        for f in os.listdir(project_root):
            if f.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(project_root, f))

        # Find PDFs in uploads folder
        if os.path.exists(upload_folder):
            for f in os.listdir(upload_folder):
                if f.lower().endswith('.pdf'):
                    pdf_files.append(os.path.join(upload_folder, f))

        if pdf_files:
            print(f"GUNICORN: Found {len(pdf_files)} PDF files for indexing.")
            documents = document_processor.process_documents(pdf_files)

            if documents:
                vector_store.add_documents(documents)
                print(f"GUNICORN: Successfully initialized vector store with {len(documents)} document chunks.")
            else:
                print("GUNICORN: Could not process any documents.")
        else:
            print("GUNICORN: No PDF files found for initialization.")
    else:
        print("GUNICORN: Vector store already contains documents. Skipping initialization.")
