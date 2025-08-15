"""
Startup service for initializing and managing the workflow engine.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI

from app.services.workflow_engine import workflow_engine

logger = logging.getLogger(__name__)


class WorkflowStartupService:
    """
    Service to manage the lifecycle of the workflow engine.
    """
    
    def __init__(self):
        self.is_started = False
    
    async def start_workflow_engine(self):
        """Start the workflow engine if not already started."""
        if self.is_started:
            logger.warning("Workflow engine already started")
            return
        
        try:
            logger.info("Starting workflow engine...")
            await workflow_engine.start()
            self.is_started = True
            logger.info("Workflow engine started successfully")
        except Exception as e:
            logger.error(f"Failed to start workflow engine: {e}")
            raise
    
    async def stop_workflow_engine(self):
        """Stop the workflow engine if running."""
        if not self.is_started:
            logger.warning("Workflow engine not started")
            return
        
        try:
            logger.info("Stopping workflow engine...")
            await workflow_engine.stop()
            self.is_started = False
            logger.info("Workflow engine stopped successfully")
        except Exception as e:
            logger.error(f"Failed to stop workflow engine: {e}")
            raise
    
    def get_status(self) -> Dict[str, Any]:
        """Get the status of the workflow startup service."""
        return {
            "startup_service_running": self.is_started,
            "workflow_engine_status": workflow_engine.get_status() if self.is_started else None
        }


# Global startup service instance
startup_service = WorkflowStartupService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager to start/stop the workflow engine.
    
    Usage in main.py:
    app = FastAPI(lifespan=lifespan)
    """
    # Startup
    logger.info("Application startup: initializing workflow engine")
    try:
        await startup_service.start_workflow_engine()
    except Exception as e:
        logger.error(f"Failed to start workflow engine during startup: {e}")
        # Decide whether to continue without workflow engine or fail
        # For now, we'll continue and the engine can be started manually
    
    yield
    
    # Shutdown
    logger.info("Application shutdown: stopping workflow engine")
    try:
        await startup_service.stop_workflow_engine()
    except Exception as e:
        logger.error(f"Failed to stop workflow engine during shutdown: {e}")


# Manual start/stop functions for development and testing
async def start_workflow_manually():
    """Manually start the workflow engine."""
    await startup_service.start_workflow_engine()


async def stop_workflow_manually():
    """Manually stop the workflow engine."""
    await startup_service.stop_workflow_engine()


async def restart_workflow():
    """Restart the workflow engine."""
    await startup_service.stop_workflow_engine()
    await asyncio.sleep(1)  # Brief pause
    await startup_service.start_workflow_engine()
