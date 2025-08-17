# Indian Legal RAG Chatbot (Flask)

A comprehensive RAG (Retrieval-Augmented Generation) chatbot for Indian Constitution and Bharatiya Nyaya Sanhita using Flask, LangChain, Google Gemini API, and ChromaDB. Optimized for easy deployment on Render.

## Features

- 📚 **Document Processing**: Upload and process PDF documents of Indian Constitution and Bharatiya Nyaya Sanhita
- 🔍 **Vector Search**: Advanced semantic search using Google's embedding models
- 🤖 **AI-Powered Responses**: Intelligent responses using Google Gemini Pro
- 🌐 **Modern Web Interface**: Clean, responsive frontend with real-time chat
- 📖 **Source Citations**: Responses include relevant document sources
- ⚡ **Flask Backend**: RESTful API built with Flask for easy deployment
- 🚀 **Render Ready**: Configured for seamless deployment on Render

## Architecture

```
├── backend/
│   ├── config.py              # Configuration settings
│   ├── document_processor.py  # PDF processing and chunking
│   ├── vector_store.py        # ChromaDB vector store management
│   ├── rag_chain.py          # RAG chain implementation
│   └── main.py               # Original FastAPI (deprecated)
├── frontend/
│   ├── index.html            # Web interface
│   └── script.js             # Frontend JavaScript
├── app.py                    # Flask application (main entry point)
├── requirements.txt          # Python dependencies
├── Procfile                  # Render deployment config
├── render.yaml              # Render service configuration
├── runtime.txt              # Python version specification
├── .env.example             # Environment variables template
└── setup.py                 # Setup script
```

## Quick Start (Local Development)

### 1. Setup Environment

```bash
# Clone or download the project
# Navigate to project directory

# Run setup script
python setup.py
```

### 2. Configure API Keys

Update the `.env` file with your Google API key:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
CHROMA_DB_PATH=./chroma_db
```

### 3. Add Documents

Place your PDF documents in the project directory:
- Indian Constitution PDF
- Bharatiya Nyaya Sanhita PDF

### 4. Start the Application

```bash
# For development
python app.py

# For production
gunicorn app:app
```

The application will be available at `http://localhost:5000`

## Render Deployment

### 1. Prepare for Deployment

1. **Fork/Clone** this repository to your GitHub account
2. **Get Google API Key** from [Google AI Studio](https://makersuite.google.com/app/apikey)

### 2. Deploy on Render

1. **Connect Repository**:
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New" → "Web Service"
   - Connect your GitHub repository

2. **Configure Service**:
   - **Name**: `indian-legal-rag-chatbot`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`

3. **Set Environment Variables**:
   - `GOOGLE_API_KEY`: Your Google Gemini API key
   - `CHROMA_DB_PATH`: `./chroma_db`

4. **Add Persistent Disk** (Optional but recommended):
   - Name: `chroma-storage`
   - Size: 1GB
   - Mount Path: `/opt/render/project/src/chroma_db`

5. **Deploy**: Click "Create Web Service"

### 3. Upload Documents

Once deployed, visit your Render URL and:
1. Upload your PDF documents using the web interface
2. Or use the "Use Existing PDFs" feature if you've included PDFs in your repository

## Usage

### Document Upload

1. **Upload New Documents**: Use the "Upload PDF Documents" button to add new legal documents
2. **Use Existing PDFs**: Click "Use Existing PDFs" to process documents already in the project directory

### Chatbot Interaction

Ask questions about:
- **Indian Constitution**: Articles, Fundamental Rights, Directive Principles, etc.
- **Bharatiya Nyaya Sanhita**: Criminal law provisions, sections, penalties, etc.

Example queries:
- "What are the fundamental rights under Article 19?"
- "Explain Section 103 of Bharatiya Nyaya Sanhita"
- "What is the procedure for amending the Constitution?"

## API Endpoints

### GET `/`
Serve the main web interface

### GET `/api/health`
Health check endpoint

### POST `/api/upload-documents`
Upload and process PDF documents
- **Body**: Multipart form data with PDF files
- **Response**: Processing status and file information

### POST `/api/query`
Query the RAG system
- **Body**: `{"question": "your question here"}`
- **Response**: AI answer with source citations

### POST `/api/initialize-with-existing-pdfs`
Process PDFs in the current directory
- **Response**: Initialization status

## Configuration

### Environment Variables

- `GOOGLE_API_KEY`: Your Google Gemini API key (required)
- `CHROMA_DB_PATH`: Path to ChromaDB storage (default: ./chroma_db)
- `PORT`: Server port (automatically set by Render)

### Model Settings

- **LLM**: Google Gemini 2.0 Flash Thinking
- **Embeddings**: Google Embedding Model (models/embedding-001)
- **Vector DB**: ChromaDB
- **Chunk Size**: 8000 characters
- **Chunk Overlap**: 1000 characters

## Dependencies

### Backend
- `Flask`: Web framework
- `Flask-CORS`: Cross-origin resource sharing
- `langchain`: LLM framework
- `langchain-google-genai`: Google Gemini integration
- `chromadb`: Vector database
- `gunicorn`: WSGI server for production
- `pypdf2`: PDF processing

### Frontend
- Vanilla JavaScript
- Tailwind CSS
- Font Awesome icons

## Development

### Project Structure

The Flask application follows a clean architecture:

1. **Document Processing**: Handles PDF loading and text chunking
2. **Vector Store**: Manages embeddings and similarity search
3. **RAG Chain**: Combines retrieval and generation
4. **Flask Routes**: API endpoints and static file serving
5. **Frontend**: Modern web interface integrated with Flask templates

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GOOGLE_API_KEY=your_api_key_here

# Run development server
python app.py
```

### Production Deployment

The application is configured for production deployment with:
- Gunicorn WSGI server
- Error handling and logging
- CORS configuration
- File upload security
- Environment-based configuration

## Troubleshooting

### Common Issues

1. **API Key Error**: Ensure your Google API key is correctly set in environment variables
2. **PDF Processing Error**: Check if PDFs are readable and not password-protected
3. **Memory Issues**: Reduce chunk size for large documents
4. **Deployment Issues**: Check Render logs for detailed error messages

### Render-Specific Issues

1. **Build Failures**: Check that all dependencies are in `requirements.txt`
2. **Runtime Errors**: Verify environment variables are set correctly
3. **Storage Issues**: Ensure persistent disk is properly configured for ChromaDB

### Logs

- **Local**: Check console output
- **Render**: View logs in Render dashboard under "Logs" tab

## Performance Optimization

- **Chunking**: Optimize chunk size based on document types
- **Caching**: ChromaDB provides built-in vector caching
- **Memory**: Monitor memory usage for large document collections
- **API Limits**: Be aware of Google API rate limits

## Security

- **File Upload**: Only PDF files are accepted
- **Input Validation**: All user inputs are validated
- **Environment Variables**: Sensitive data stored in environment variables
- **CORS**: Configured for secure cross-origin requests

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## Support

For issues related to:
- **Google API**: Check [Google AI documentation](https://ai.google.dev/)
- **Render Deployment**: Check [Render documentation](https://render.com/docs)
- **LangChain**: Check [LangChain documentation](https://python.langchain.com/)