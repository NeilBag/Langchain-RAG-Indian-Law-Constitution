from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
import shutil
from werkzeug.utils import secure_filename
from backend.document_processor import DocumentProcessor
from backend.vector_store import VectorStore
from backend.rag_chain import RAGChain

app = Flask(__name__, 
           template_folder='frontend',
           static_folder='frontend')
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Initialize components
document_processor = DocumentProcessor()
vector_store = VectorStore()

# Auto-initialize with existing PDFs if vector store is empty
def auto_initialize_documents():
    """Auto-initialize documents on startup if vector store is empty"""
    try:
        if vector_store.is_empty():
            print("Vector store is empty. Auto-initializing with existing PDFs...")
            
            # Find PDF files in current directory and uploads folder
            pdf_files = []
            
            # Check current directory
            for f in os.listdir("."):
                if f.lower().endswith('.pdf'):
                    pdf_files.append(f)
            
            # Check uploads directory
            if os.path.exists(app.config['UPLOAD_FOLDER']):
                for f in os.listdir(app.config['UPLOAD_FOLDER']):
                    if f.lower().endswith('.pdf'):
                        pdf_files.append(os.path.join(app.config['UPLOAD_FOLDER'], f))
            
            if pdf_files:
                print(f"Found {len(pdf_files)} PDF files: {pdf_files}")
                documents = document_processor.process_documents(pdf_files)
                
                if documents:
                    vector_store.add_documents(documents)
                    print(f"Auto-initialized with {len(documents)} document chunks from {len(pdf_files)} files")
                else:
                    print("No documents could be processed during auto-initialization")
            else:
                print("No PDF files found for auto-initialization")
        else:
            print("Vector store already contains documents. Skipping auto-initialization.")
    except Exception as e:
        print(f"Error during auto-initialization: {str(e)}")

# Perform auto-initialization
# The line below is commented out to prevent long startup times on Render,
# which can cause deployment timeouts. Initialization can be triggered
# manually via the /api/initialize-with-existing-pdfs endpoint.
# auto_initialize_documents()

# Initialize RAG chain after documents are loaded
rag_chain = RAGChain()

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/script.js')
def serve_js():
    """Serve the JavaScript file"""
    return send_from_directory('frontend', 'script.js', mimetype='application/javascript')

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "Indian Legal RAG Chatbot API"})

@app.route('/api/upload-documents', methods=['POST'])
def upload_documents():
    """Upload and process PDF documents"""
    try:
        if 'files' not in request.files:
            return jsonify({"error": "No files provided"}), 400
        
        files = request.files.getlist('files')
        if not files or all(f.filename == '' for f in files):
            return jsonify({"error": "No files selected"}), 400
        
        uploaded_files = []
        
        # Save uploaded files
        for file in files:
            if file and file.filename:
                if not file.filename.lower().endswith('.pdf'):
                    return jsonify({"error": f"Only PDF files are allowed. {file.filename} is not a PDF."}), 400
                
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                uploaded_files.append(file_path)
        
        # Process documents
        documents = document_processor.process_documents(uploaded_files)
        
        if not documents:
            return jsonify({"error": "No documents could be processed"}), 400
        
        # Add to vector store
        vector_store.add_documents(documents)
        
        return jsonify({
            "message": f"Successfully processed {len(documents)} document chunks from {len(uploaded_files)} files",
            "files_processed": [os.path.basename(f) for f in uploaded_files]
        })
        
    except Exception as e:
        return jsonify({"error": f"Error processing documents: {str(e)}"}), 500

@app.route('/api/query', methods=['POST'])
def query_documents():
    """Query the RAG system with context awareness"""
    try:
        data = request.get_json()
        
        if not data or 'question' not in data:
            return jsonify({"error": "Question is required"}), 400
        
        question = data['question'].strip()
        if not question:
            return jsonify({"error": "Question cannot be empty"}), 400
        
        # Handle session management
        session_id = data.get('session_id')
        if session_id:
            rag_chain.load_conversation(session_id)
        
        result = rag_chain.query(question)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": f"Error processing query: {str(e)}"}), 500

@app.route('/api/new-conversation', methods=['POST'])
def start_new_conversation():
    """Start a new conversation session"""
    try:
        session_id = rag_chain.start_new_conversation()
        return jsonify({
            "session_id": session_id,
            "message": "New conversation started"
        })
    except Exception as e:
        return jsonify({"error": f"Error starting new conversation: {str(e)}"}), 500

@app.route('/api/conversation-history/<session_id>', methods=['GET'])
def get_conversation_history(session_id):
    """Get conversation history for a session"""
    try:
        if rag_chain.load_conversation(session_id):
            history = rag_chain.get_conversation_history()
            return jsonify({
                "session_id": session_id,
                "history": history
            })
        else:
            return jsonify({"error": "Session not found"}), 404
    except Exception as e:
        return jsonify({"error": f"Error getting conversation history: {str(e)}"}), 500

@app.route('/api/recent-sessions', methods=['GET'])
def get_recent_sessions():
    """Get list of recent conversation sessions"""
    try:
        limit = request.args.get('limit', 10, type=int)
        sessions = rag_chain.get_recent_sessions(limit)
        return jsonify({"sessions": sessions})
    except Exception as e:
        return jsonify({"error": f"Error getting recent sessions: {str(e)}"}), 500

@app.route('/api/initialize-with-existing-pdfs', methods=['POST'])
def initialize_with_existing_pdfs():
    """Initialize the system with PDFs in the current directory"""
    try:
        # Find PDF files in current directory and uploads folder
        pdf_files = []
        
        # Check current directory
        for f in os.listdir("."):
            if f.lower().endswith('.pdf'):
                pdf_files.append(f)
        
        # Check uploads directory
        if os.path.exists(app.config['UPLOAD_FOLDER']):
            for f in os.listdir(app.config['UPLOAD_FOLDER']):
                if f.lower().endswith('.pdf'):
                    pdf_files.append(os.path.join(app.config['UPLOAD_FOLDER'], f))
        
        if not pdf_files:
            return jsonify({"message": "No PDF files found in current directory or uploads folder"})
        
        # Process the PDF files
        documents = document_processor.process_documents(pdf_files)
        
        if not documents:
            return jsonify({"error": "No documents could be processed"}), 400
        
        # Add to vector store
        vector_store.add_documents(documents)
        
        return jsonify({
            "message": f"Successfully initialized with {len(documents)} document chunks from {len(pdf_files)} files",
            "files_processed": [os.path.basename(f) for f in pdf_files]
        })
        
    except Exception as e:
        return jsonify({"error": f"Error initializing system: {str(e)}"}), 500

@app.errorhandler(413)
def too_large(e):
    return jsonify({"error": "File too large. Maximum size is 50MB."}), 413

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500
