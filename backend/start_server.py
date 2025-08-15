#!/usr/bin/env python3
"""
Start the FastAPI development server with proper configuration
"""
import sys
import os
from pathlib import Path

# Add current directory to Python path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Set environment variable for better debugging
os.environ["PYTHONPATH"] = str(current_dir)

if __name__ == "__main__":
    import uvicorn
    
    # Import our FastAPI app
    from app.main import app
    
    print("Starting nxtLvl backend server...")
    print("API docs will be available at: http://127.0.0.1:8001/docs")
    print("Health check at: http://127.0.0.1:8001/api/health")
    print("Automations API at: http://127.0.0.1:8001/api/automations/")
    
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8001,
        reload=True,
        reload_dirs=[str(current_dir)],
        log_level="info"
    )
