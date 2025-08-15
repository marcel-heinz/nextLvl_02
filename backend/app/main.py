from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import sys
from pathlib import Path

# Load environment variables
load_dotenv()

# Ensure package imports work when running `python app/main.py`
if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[1]))

# Import workflow lifespan manager
from app.services.workflow_startup import lifespan

# Create FastAPI app with workflow lifecycle management
app = FastAPI(
    title="nxtLvl API",
    description="Backend API for nxtLvl application with automated workflow processing",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.routes.automations import router as automations_router  # noqa: E402
from app.routes.workflow import router as workflow_router  # noqa: E402

app.include_router(automations_router)
app.include_router(workflow_router)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "nxtLvl API is running!", "status": "healthy"}

@app.get("/api/health")
async def health_check():
    """Detailed health check including workflow status"""
    from app.services.workflow_startup import startup_service
    from app.services.workflow_engine import workflow_engine
    
    workflow_status = "unknown"
    try:
        if startup_service.is_started:
            engine_status = workflow_engine.get_status()
            if engine_status["engine_running"]:
                workflow_status = "running"
            else:
                workflow_status = "stopped"
        else:
            workflow_status = "not_started"
    except Exception as e:
        workflow_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "workflow_engine": workflow_status
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)
