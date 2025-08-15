"""
Workflow management routes for monitoring and controlling the automation pipeline.
"""

from __future__ import annotations

from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from app.services.workflow_engine import workflow_engine, WorkerStatus
from app.services.workflow_startup import startup_service
from app.models.automation import Stage

router = APIRouter(prefix="/api/workflow", tags=["workflow"])


class WorkflowStatusResponse(BaseModel):
    """Response model for workflow status."""
    engine_running: bool
    startup_service_running: bool
    processors: Dict[str, Dict[str, Any]]
    
    
class TriggerStageRequest(BaseModel):
    """Request model for triggering stage processing."""
    stage: Stage


class WorkflowControlResponse(BaseModel):
    """Response model for workflow control operations."""
    success: bool
    message: str


@router.get("/status", response_model=WorkflowStatusResponse)
async def get_workflow_status() -> WorkflowStatusResponse:
    """Get the current status of the workflow engine and all processors."""
    startup_status = startup_service.get_status()
    engine_status = workflow_engine.get_status()
    
    return WorkflowStatusResponse(
        engine_running=engine_status["engine_running"],
        startup_service_running=startup_status["startup_service_running"],
        processors=engine_status["processors"]
    )


@router.post("/start", response_model=WorkflowControlResponse)
async def start_workflow_engine(background_tasks: BackgroundTasks) -> WorkflowControlResponse:
    """Start the workflow engine."""
    try:
        if startup_service.is_started:
            return WorkflowControlResponse(
                success=False,
                message="Workflow engine is already running"
            )
        
        # Start in background to avoid blocking the response
        background_tasks.add_task(startup_service.start_workflow_engine)
        
        return WorkflowControlResponse(
            success=True,
            message="Workflow engine start initiated"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start workflow engine: {str(e)}")


@router.post("/stop", response_model=WorkflowControlResponse)
async def stop_workflow_engine(background_tasks: BackgroundTasks) -> WorkflowControlResponse:
    """Stop the workflow engine."""
    try:
        if not startup_service.is_started:
            return WorkflowControlResponse(
                success=False,
                message="Workflow engine is not running"
            )
        
        # Stop in background to avoid blocking the response
        background_tasks.add_task(startup_service.stop_workflow_engine)
        
        return WorkflowControlResponse(
            success=True,
            message="Workflow engine stop initiated"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop workflow engine: {str(e)}")


@router.post("/restart", response_model=WorkflowControlResponse)
async def restart_workflow_engine(background_tasks: BackgroundTasks) -> WorkflowControlResponse:
    """Restart the workflow engine."""
    try:
        async def restart_task():
            await startup_service.stop_workflow_engine()
            await startup_service.start_workflow_engine()
        
        background_tasks.add_task(restart_task)
        
        return WorkflowControlResponse(
            success=True,
            message="Workflow engine restart initiated"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to restart workflow engine: {str(e)}")


@router.post("/trigger-stage", response_model=WorkflowControlResponse)
async def trigger_stage_processing(request: TriggerStageRequest) -> WorkflowControlResponse:
    """
    Manually trigger processing for a specific stage.
    
    This will cause the stage processor to immediately check for work
    instead of waiting for the next poll interval.
    """
    try:
        if not startup_service.is_started:
            raise HTTPException(status_code=400, detail="Workflow engine is not running")
        
        await workflow_engine.trigger_stage_check(request.stage)
        
        return WorkflowControlResponse(
            success=True,
            message=f"Triggered processing check for stage: {request.stage}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to trigger stage processing: {str(e)}")


@router.get("/stages")
async def get_stage_info() -> Dict[str, Any]:
    """Get information about all workflow stages."""
    return {
        "stages": [stage.value for stage in Stage],
        "stage_flow": [
            {"from": Stage.NEW, "to": Stage.CLASSIFICATION},
            {"from": Stage.CLASSIFICATION, "to": Stage.DATA_EXTRACTION},
            {"from": Stage.DATA_EXTRACTION, "to": Stage.PROCESSING},
            {"from": Stage.PROCESSING, "to": Stage.DONE},
        ],
        "description": {
            Stage.NEW: "Items uploaded and ready for classification",
            Stage.CLASSIFICATION: "AI classification of document type/content",
            Stage.DATA_EXTRACTION: "Extract structured data from classified documents",
            Stage.PROCESSING: "Final processing and business rule application",
            Stage.DONE: "Completed items ready for export/usage"
        }
    }


@router.get("/metrics")
async def get_workflow_metrics() -> Dict[str, Any]:
    """Get workflow performance metrics."""
    try:
        # Get current queue lengths from database
        from app.utils.supabase_client import supabase_service
        
        stage_counts = {}
        for stage in Stage:
            automations = await supabase_service.get_automations_by_stage(stage)
            stage_counts[stage.value] = len(automations)
        
        # Get processor status
        engine_status = workflow_engine.get_status()
        
        processing_counts = {}
        for stage_name, processor_info in engine_status["processors"].items():
            processing_counts[stage_name] = {
                "status": processor_info["status"],
                "current_item": processor_info["current_automation"] is not None,
                "poll_interval": processor_info["poll_interval"]
            }
        
        return {
            "queue_lengths": stage_counts,
            "processor_status": processing_counts,
            "engine_running": engine_status["engine_running"],
            "total_items": sum(stage_counts.values())
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")


@router.post("/move-to-next-stage/{automation_id}", response_model=WorkflowControlResponse)
async def manually_move_to_next_stage(automation_id: str) -> WorkflowControlResponse:
    """
    Manually move an automation to the next stage.
    
    This bypasses the normal processing and immediately moves the item.
    Useful for testing or handling stuck items.
    """
    try:
        from app.utils.supabase_client import supabase_service
        from app.models.automation import AutomationUpdate
        
        # Get current automation
        automation = await supabase_service.get_automation(automation_id)
        if not automation:
            raise HTTPException(status_code=404, detail="Automation not found")
        
        # Determine next stage
        stage_order = [Stage.NEW, Stage.CLASSIFICATION, Stage.DATA_EXTRACTION, Stage.PROCESSING, Stage.DONE]
        try:
            current_index = stage_order.index(automation.stage)
            if current_index < len(stage_order) - 1:
                next_stage = stage_order[current_index + 1]
                
                # Update automation
                update_data = AutomationUpdate(stage=next_stage)
                updated = await supabase_service.update_automation(automation_id, update_data)
                
                if updated:
                    return WorkflowControlResponse(
                        success=True,
                        message=f"Moved automation from {automation.stage} to {next_stage}"
                    )
                else:
                    raise HTTPException(status_code=500, detail="Failed to update automation")
            else:
                return WorkflowControlResponse(
                    success=False,
                    message="Automation is already in the final stage"
                )
                
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid current stage")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to move automation: {str(e)}")
