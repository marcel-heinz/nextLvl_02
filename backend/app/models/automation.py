from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field


class Stage(str, Enum):
    NEW = "New"
    CLASSIFICATION = "Classification"
    DATA_EXTRACTION = "Data Extraction"
    PROCESSING = "Processing"
    DONE = "Done"


class AutomationBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    stage: Stage = Stage.NEW
    file_name: Optional[str] = Field(None, max_length=255)
    file_url: Optional[str] = Field(None, max_length=1000)
    blob_name: Optional[str] = Field(None, max_length=255)
    
    # Classification fields
    lob: Optional[str] = Field(None, max_length=255)
    process: Optional[str] = Field(None, max_length=255)
    classification_status: Optional[str] = Field(None, max_length=50)
    case_parameters: Optional[Dict[str, Any]] = None


class AutomationCreate(AutomationBase):
    pass


class AutomationUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    stage: Optional[Stage] = None
    file_name: Optional[str] = Field(None, max_length=255)
    file_url: Optional[str] = Field(None, max_length=1000)
    blob_name: Optional[str] = Field(None, max_length=255)
    
    # Classification fields
    lob: Optional[str] = Field(None, max_length=255)
    process: Optional[str] = Field(None, max_length=255)
    classification_status: Optional[str] = Field(None, max_length=50)
    case_parameters: Optional[Dict[str, Any]] = None


class Automation(AutomationBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Pipeline Configuration Models
class LOBProcessPair(BaseModel):
    lob: str = Field(..., min_length=1, max_length=255)
    process: str = Field(..., min_length=1, max_length=255)


class LLMParams(BaseModel):
    temperature: float = Field(0.0, ge=0.0, le=1.0)
    max_tokens: int = Field(500, ge=1, le=8000)


class PipelineConfigBase(BaseModel):
    lob_prompt: str = Field(..., min_length=1, max_length=2000)
    process_prompt: str = Field(..., min_length=1, max_length=2000)
    lob_process_pairs: list[LOBProcessPair] = Field(..., min_items=1)
    llm_params: LLMParams


class PipelineConfigCreate(PipelineConfigBase):
    pass


class PipelineConfigUpdate(BaseModel):
    lob_prompt: Optional[str] = Field(None, min_length=1, max_length=2000)
    process_prompt: Optional[str] = Field(None, min_length=1, max_length=2000)
    lob_process_pairs: Optional[list[LOBProcessPair]] = Field(None, min_items=1)
    llm_params: Optional[LLMParams] = None


class PipelineConfig(PipelineConfigBase):
    id: str
    version: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


