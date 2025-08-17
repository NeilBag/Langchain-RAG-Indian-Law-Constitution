# Deployment Guide for Render

## Prerequisites

1. **Google API Key**: Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. **GitHub Repository**: Fork or upload this code to your GitHub account
3. **Render Account**: Sign up at [render.com](https://render.com)

## Step-by-Step Deployment

### 1. Prepare Your Repository

Ensure your repository contains:
- ✅ `app.py` (Flask application)
- ✅ `requirements.txt` (Python dependencies)
- ✅ `Procfile` (Render configuration)
- ✅ `runtime.txt` (Python version)
- ✅ All backend and frontend files

### 2. Deploy on Render

1. **Login to Render Dashboard**
   - Go to https://dashboard.render.com/
   - Sign in with your GitHub account

2. **Create New Web Service**
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Select the repository containing this code

3. **Configure Service Settings**
   ```
   Name: indian-legal-rag-chatbot
   Environment: Python 3
   Branch: main (or your default branch)
   Root Directory: . (leave empty)
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn app:app
   ```

4. **Set Environment Variables**
   - Click "Environment" tab
   - Add the following variables:
     ```
     GOOGLE_API_KEY = your_actual_google_api_key_here
     CHROMA_DB_PATH = ./chroma_db
     ```

5. **Configure Persistent Storage (Recommended)**
   - Click "Disks" tab
   - Add disk:
     ```
     Name: chroma-storage
     Mount Path: /opt/render/project/src/chroma_db
     Size: 1 GB
     ```

6. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment to complete (5-10 minutes)

### 3. Post-Deployment Setup

1. **Access Your Application**
   - Your app will be available at: `https://your-service-name.onrender.com`
   - The URL will be shown in your Render dashboard

2. **Upload Documents**
   - Visit your deployed application
   - Use the "Upload PDF Documents" feature to add your legal documents
   - Or place PDFs in your repository and use "Use Existing PDFs"

3. **Test the Chatbot**
   - Try asking questions about Indian Constitution or Bharatiya Nyaya Sanhita
   - Verify that responses include proper source citations

## Environment Variables Explained

| Variable | Description | Example |
|----------|-------------|---------|
| `GOOGLE_API_KEY` | Your Google Gemini API key | `AIzaSyC...` |
| `CHROMA_DB_PATH` | Path for vector database storage | `./chroma_db` |
| `PORT` | Server port (auto-set by Render) | `10000` |

## Troubleshooting

### Common Deployment Issues

1. **Build Fails**
   ```
   Solution: Check that requirements.txt contains all dependencies
   Check logs: Render Dashboard → Your Service → Logs
   ```

2. **App Crashes on Start**
   ```
   Solution: Verify environment variables are set correctly
   Check: GOOGLE_API_KEY is valid and has proper permissions
   ```

3. **PDF Upload Fails**
   ```
   Solution: Ensure persistent disk is configured
   Check: File size limits (50MB max)
   ```

4. **ChromaDB Errors**
   ```
   Solution: Verify persistent storage is mounted correctly
   Path should be: /opt/render/project/src/chroma_db
   ```

### Performance Optimization

1. **Cold Starts**
   - Render free tier has cold starts
   - Consider upgrading to paid plan for better performance

2. **Memory Usage**
   - Monitor memory usage in Render dashboard
   - Reduce chunk size if memory issues occur

3. **API Rate Limits**
   - Google API has rate limits
   - Implement caching if needed

## Monitoring

### Health Checks
- Endpoint: `https://your-app.onrender.com/api/health`
- Should return: `{"status": "healthy", "message": "Indian Legal RAG Chatbot API"}`

### Logs
- Access logs in Render Dashboard → Your Service → Logs
- Monitor for errors and performance issues

## Scaling

### Horizontal Scaling
- Render supports auto-scaling on paid plans
- Configure based on traffic patterns

### Database Scaling
- Increase persistent disk size as document collection grows
- Monitor ChromaDB performance

## Security Best Practices

1. **Environment Variables**
   - Never commit API keys to repository
   - Use Render's environment variable system

2. **File Uploads**
   - Only PDF files are accepted
   - 50MB file size limit enforced

3. **CORS Configuration**
   - Configured for secure cross-origin requests
   - Adjust if needed for custom domains

## Custom Domain (Optional)

1. **Add Custom Domain**
   - Go to Render Dashboard → Your Service → Settings
   - Add your custom domain
   - Configure DNS records as instructed

2. **SSL Certificate**
   - Render provides free SSL certificates
   - Automatically configured for custom domains

## Backup and Recovery

1. **Code Backup**
   - Code is backed up in your GitHub repository
   - Ensure regular commits

2. **Data Backup**
   - ChromaDB data is stored on persistent disk
   - Consider periodic backups for important document collections

3. **Environment Variables**
   - Document your environment variables
   - Store securely (not in repository)

## Cost Optimization

1. **Free Tier Limits**
   - 750 hours/month free
   - Automatic sleep after 15 minutes of inactivity

2. **Paid Plans**
   - $7/month for always-on service
   - Better performance and no cold starts

3. **Storage Costs**
   - Persistent disks: $0.25/GB/month
   - Monitor usage and optimize as needed

## Support Resources

- **Render Documentation**: https://render.com/docs
- **Google AI Documentation**: https://ai.google.dev/
- **LangChain Documentation**: https://python.langchain.com/
- **Flask Documentation**: https://flask.palletsprojects.com/