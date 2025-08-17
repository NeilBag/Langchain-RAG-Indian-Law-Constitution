#!/usr/bin/env python3
"""
Setup script for Indian Legal RAG Chatbot (Flask Version)
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def setup_environment():
    """Setup the development environment"""
    print("🚀 Setting up Indian Legal RAG Chatbot Environment (Flask)")
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("\n📝 Creating .env file from template...")
        if os.path.exists('.env.example'):
            with open('.env.example', 'r') as src, open('.env', 'w') as dst:
                dst.write(src.read())
            print("✅ .env file created. Please update it with your Google API key.")
        else:
            print("❌ .env.example not found")
    
    # Install Python dependencies
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        return False
    
    # Create necessary directories
    directories = ['uploads', 'chroma_db']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"📁 Created directory: {directory}")
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Update the .env file with your Google API key")
    print("2. Place your PDF documents in the project directory")
    print("3. For local development: python app.py")
    print("4. For production: gunicorn app:app")
    print("5. Access the app at http://localhost:5000")
    
    return True

if __name__ == "__main__":
    setup_environment()