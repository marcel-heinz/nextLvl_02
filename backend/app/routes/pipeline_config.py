"""
Pipeline Configuration API endpoints
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from datetime import datetime

from app.models.automation import (
    PipelineConfig, 
    PipelineConfigCreate, 
    PipelineConfigUpdate,
    LOBProcessPair,
    LLMParams
)
from app.utils.supabase_client import supabase_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/pipeline-config", tags=["pipeline-config"])


@router.get("/", response_model=Optional[PipelineConfig])
async def get_current_config() -> Optional[PipelineConfig]:
    """Get the current/latest pipeline configuration."""
    try:
        config_data = await supabase_service.get_latest_pipeline_config()
        
        if not config_data:
            return None
        
        # Transform the data to match our Pydantic models
        return PipelineConfig(
            id=config_data['id'],
            lob_prompt=config_data['lob_prompt'],
            process_prompt=config_data['process_prompt'],
            lob_process_pairs=[
                LOBProcessPair(**pair) for pair in config_data['lob_process_pairs']
            ],
            llm_params=LLMParams(**config_data['llm_params']),
            version=config_data['version'],
            created_at=config_data['created_at'],
            updated_at=config_data['updated_at']
        )
        
    except Exception as e:
        logger.error(f"Failed to get pipeline config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get pipeline config: {str(e)}"
        )


@router.post("/", response_model=PipelineConfig)
async def create_or_update_config(config: PipelineConfigCreate) -> PipelineConfig:
    """Create or update pipeline configuration."""
    try:
        # Get current config to determine next version
        current_config = await supabase_service.get_latest_pipeline_config()
        next_version = (current_config.get('version', 0) + 1) if current_config else 1
        
        # Validate LOB-Process pairs are unique
        pairs = config.lob_process_pairs
        pair_strings = [f"{pair.lob}|{pair.process}" for pair in pairs]
        if len(pair_strings) != len(set(pair_strings)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Duplicate LOB-Process pairs are not allowed"
            )
        
        # Prepare data for database
        config_data = {
            "lob_prompt": config.lob_prompt,
            "process_prompt": config.process_prompt,
            "lob_process_pairs": [pair.model_dump() for pair in config.lob_process_pairs],
            "llm_params": config.llm_params.model_dump(),
            "version": next_version,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Save to database
        result = await supabase_service.create_pipeline_config(config_data)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save pipeline configuration"
            )
        
        # Return the created config
        return PipelineConfig(
            id=result['id'],
            lob_prompt=result['lob_prompt'],
            process_prompt=result['process_prompt'],
            lob_process_pairs=[
                LOBProcessPair(**pair) for pair in result['lob_process_pairs']
            ],
            llm_params=LLMParams(**result['llm_params']),
            version=result['version'],
            created_at=result['created_at'],
            updated_at=result['updated_at']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create/update pipeline config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create/update pipeline config: {str(e)}"
        )


@router.get("/history", response_model=List[PipelineConfig])
async def get_config_history(limit: int = 10) -> List[PipelineConfig]:
    """Get pipeline configuration history."""
    try:
        configs = await supabase_service.get_pipeline_config_history(limit)
        
        return [
            PipelineConfig(
                id=config['id'],
                lob_prompt=config['lob_prompt'],
                process_prompt=config['process_prompt'],
                lob_process_pairs=[
                    LOBProcessPair(**pair) for pair in config['lob_process_pairs']
                ],
                llm_params=LLMParams(**config['llm_params']),
                version=config['version'],
                created_at=config['created_at'],
                updated_at=config['updated_at']
            )
            for config in configs
        ]
        
    except Exception as e:
        logger.error(f"Failed to get config history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get config history: {str(e)}"
        )


@router.delete("/")
async def delete_all_configs():
    """Delete all pipeline configurations (for testing/reset purposes)."""
    try:
        result = await supabase_service.delete_all_pipeline_configs()
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete configurations"
            )
        
        return {"message": "All pipeline configurations deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete configs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete configs: {str(e)}"
        )
