from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

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


class AutomationCreate(AutomationBase):
    pass


class AutomationUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    stage: Optional[Stage] = None
    file_name: Optional[str] = Field(None, max_length=255)
    file_url: Optional[str] = Field(None, max_length=1000)
    blob_name: Optional[str] = Field(None, max_length=255)


class Automation(AutomationBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


