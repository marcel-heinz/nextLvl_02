from __future__ import annotations

from typing import List

from fastapi import APIRouter, HTTPException, Response, UploadFile, File, Form

from app.models.automation import (
    Automation,
    AutomationCreate,
    AutomationUpdate,
    Stage,
)
from app.utils.azure_storage import azure_storage
from app.utils.supabase_client import supabase_service


router = APIRouter(prefix="/api/automations", tags=["automations"])


# No longer needed - using Supabase for persistence


@router.get("/", response_model=List[Automation])
async def list_automations() -> List[Automation]:
    return await supabase_service.get_automations()


@router.post("/", response_model=Automation, status_code=201)
async def create_automation(payload: AutomationCreate) -> Automation:
    automation = await supabase_service.create_automation(payload)
    if not automation:
        raise HTTPException(status_code=500, detail="Failed to create automation")
    return automation


@router.post("/upload", response_model=Automation, status_code=201)
async def create_automation_with_file(
    file: UploadFile = File(...),
    title: str = Form(None),
) -> Automation:
    """Create automation with file upload to Azure Storage"""
    try:
        # Upload file to Azure Storage
        blob_name, file_url = await azure_storage.upload_file(file)
        
        # Use filename as title if not provided
        final_title = title or file.filename.replace(".pdf", "").replace(".jpg", "").replace(".png", "")
        
        # Create automation data with proper stage value
        automation_data = AutomationCreate(
            title=final_title,
            stage=Stage.NEW,  # This will use the enum's string value
            file_name=file.filename,
            file_url=file_url,
            blob_name=blob_name,
        )
        
        automation = await supabase_service.create_automation(automation_data)
        if not automation:
            raise HTTPException(status_code=500, detail="Failed to create automation in database")
        
        # Trigger workflow processing for the Classification stage
        # This will cause the Classification processor to check for new work immediately
        try:
            from app.services.workflow_engine import workflow_engine
            from app.services.workflow_startup import startup_service
            
            if startup_service.is_started:
                await workflow_engine.trigger_stage_check(Stage.CLASSIFICATION)
        except Exception as workflow_error:
            # Don't fail the upload if workflow trigger fails
            print(f"Warning: Failed to trigger workflow after upload: {workflow_error}")
        
        return automation
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create automation: {str(e)}")


@router.get("/{automation_id}", response_model=Automation)
async def get_automation(automation_id: str) -> Automation:
    automation = await supabase_service.get_automation(automation_id)
    if not automation:
        raise HTTPException(status_code=404, detail="Automation not found")
    return automation


@router.patch("/{automation_id}", response_model=Automation)
async def update_automation(automation_id: str, payload: AutomationUpdate) -> Automation:
    updated = await supabase_service.update_automation(automation_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="Automation not found")
    return updated


@router.delete("/{automation_id}", status_code=204, response_class=Response)
async def delete_automation(automation_id: str) -> Response:
    # First, get the automation to retrieve blob_name
    automation = await supabase_service.get_automation(automation_id)
    if not automation:
        raise HTTPException(status_code=404, detail="Automation not found")
    
    # Delete from Azure Blob Storage if blob exists
    if automation.blob_name:
        try:
            deleted_from_azure = azure_storage.delete_file(automation.blob_name)
            if not deleted_from_azure:
                print(f"Warning: Failed to delete blob {automation.blob_name} from Azure Storage")
        except Exception as e:
            print(f"Warning: Error deleting blob from Azure Storage: {e}")
            # Continue with database deletion even if Azure deletion fails
    
    # Delete from database
    success = await supabase_service.delete_automation(automation_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete automation from database")
    
    return Response(status_code=204)


