"""
Workflow Engine for managing automation pipeline stages.

This implements a pull-based architecture where each stage has workers
that actively poll for work, process it, and move items to the next stage.
"""

from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Type
from enum import Enum

from app.models.automation import Stage, Automation
from app.utils.supabase_client import supabase_service

logger = logging.getLogger(__name__)


class WorkerStatus(str, Enum):
    IDLE = "idle"
    PROCESSING = "processing"
    ERROR = "error"
    STOPPED = "stopped"


class BaseStageProcessor(ABC):
    """Base class for stage-specific processors."""
    
    def __init__(self, stage: Stage, poll_interval: int = 5):
        self.stage = stage
        self.poll_interval = poll_interval
        self.status = WorkerStatus.IDLE
        self.is_running = False
        self.current_automation_id: Optional[str] = None
        
    @abstractmethod
    async def process_automation(self, automation: Automation) -> bool:
        """
        Process an automation for this stage.
        
        Args:
            automation: The automation to process
            
        Returns:
            bool: True if processing succeeded, False otherwise
        """
        pass
    
    def get_next_stage(self) -> Optional[Stage]:
        """Get the next stage in the workflow."""
        stage_order = [Stage.NEW, Stage.CLASSIFICATION, Stage.DATA_EXTRACTION, Stage.PROCESSING, Stage.DONE]
        try:
            current_index = stage_order.index(self.stage)
            if current_index < len(stage_order) - 1:
                return stage_order[current_index + 1]
        except ValueError:
            pass
        return None
    
    async def start(self):
        """Start the worker loop."""
        self.is_running = True
        logger.info(f"Starting {self.stage} worker")
        
        while self.is_running:
            try:
                await self._process_next_item()
                await asyncio.sleep(self.poll_interval)
            except Exception as e:
                logger.error(f"Error in {self.stage} worker: {e}")
                self.status = WorkerStatus.ERROR
                await asyncio.sleep(self.poll_interval * 2)  # Back off on error
    
    async def stop(self):
        """Stop the worker loop."""
        self.is_running = False
        self.status = WorkerStatus.STOPPED
        logger.info(f"Stopped {self.stage} worker")
    
    async def _process_next_item(self):
        """Process the next available item for this stage."""
        try:
            # Get next automation to process
            automation = await self._get_next_automation()
            if not automation:
                self.status = WorkerStatus.IDLE
                return
            
            self.status = WorkerStatus.PROCESSING
            self.current_automation_id = automation.id
            
            logger.info(f"Processing automation {automation.id} in stage {self.stage}")
            
            # Process the automation
            success = await self.process_automation(automation)
            
            if success:
                # Move to next stage
                next_stage = self.get_next_stage()
                if next_stage:
                    await self._move_to_next_stage(automation.id, next_stage)
                    logger.info(f"Moved automation {automation.id} from {self.stage} to {next_stage}")
                else:
                    logger.info(f"Automation {automation.id} completed workflow")
            else:
                logger.error(f"Failed to process automation {automation.id} in stage {self.stage}")
                # Could implement retry logic here
                
        except Exception as e:
            logger.error(f"Error processing item in {self.stage}: {e}")
        finally:
            self.current_automation_id = None
            self.status = WorkerStatus.IDLE
    
    async def _get_next_automation(self) -> Optional[Automation]:
        """Get the next automation to process for this stage."""
        automations = await supabase_service.get_automations_by_stage(self.stage, limit=1)
        return automations[0] if automations else None
    
    async def _move_to_next_stage(self, automation_id: str, next_stage: Stage):
        """Move automation to the next stage."""
        from app.models.automation import AutomationUpdate
        
        update_data = AutomationUpdate(stage=next_stage)
        await supabase_service.update_automation(automation_id, update_data)


class ClassificationProcessor(BaseStageProcessor):
    """Processor for the Classification stage."""
    
    def __init__(self):
        super().__init__(Stage.CLASSIFICATION, poll_interval=3)
    
    async def process_automation(self, automation: Automation) -> bool:
        """
        Classify the document/file.
        
        This is where you'd integrate with your classification AI/ML models.
        """
        try:
            logger.info(f"Classifying automation {automation.id}: {automation.title}")
            
            # TODO: Implement actual classification logic
            # For now, simulate processing time
            await asyncio.sleep(2)
            
            # Example classification logic:
            # 1. Download file from Azure Storage using automation.file_url
            # 2. Send to classification model/service
            # 3. Store classification results (you might want to add fields to store results)
            
            logger.info(f"Classification completed for automation {automation.id}")
            return True
            
        except Exception as e:
            logger.error(f"Classification failed for automation {automation.id}: {e}")
            return False


class DataExtractionProcessor(BaseStageProcessor):
    """Processor for the Data Extraction stage."""
    
    def __init__(self):
        super().__init__(Stage.DATA_EXTRACTION, poll_interval=3)
    
    async def process_automation(self, automation: Automation) -> bool:
        """
        Extract data from the classified document.
        """
        try:
            logger.info(f"Extracting data from automation {automation.id}: {automation.title}")
            
            # TODO: Implement actual data extraction logic
            # Simulate processing time
            await asyncio.sleep(3)
            
            # Example data extraction logic:
            # 1. Use classification results to determine extraction strategy
            # 2. Apply appropriate OCR/parsing techniques
            # 3. Extract structured data
            # 4. Validate extracted data
            
            logger.info(f"Data extraction completed for automation {automation.id}")
            return True
            
        except Exception as e:
            logger.error(f"Data extraction failed for automation {automation.id}: {e}")
            return False


class ProcessingProcessor(BaseStageProcessor):
    """Processor for the Processing stage."""
    
    def __init__(self):
        super().__init__(Stage.PROCESSING, poll_interval=5)
    
    async def process_automation(self, automation: Automation) -> bool:
        """
        Final processing of the automation.
        """
        try:
            logger.info(f"Final processing of automation {automation.id}: {automation.title}")
            
            # TODO: Implement actual processing logic
            # Simulate processing time
            await asyncio.sleep(4)
            
            # Example processing logic:
            # 1. Apply business rules to extracted data
            # 2. Generate outputs (reports, API calls, etc.)
            # 3. Store final results
            
            logger.info(f"Processing completed for automation {automation.id}")
            return True
            
        except Exception as e:
            logger.error(f"Processing failed for automation {automation.id}: {e}")
            return False


class WorkflowEngine:
    """
    Main workflow engine that manages all stage processors.
    """
    
    def __init__(self):
        self.processors: Dict[Stage, BaseStageProcessor] = {
            Stage.CLASSIFICATION: ClassificationProcessor(),
            Stage.DATA_EXTRACTION: DataExtractionProcessor(),
            Stage.PROCESSING: ProcessingProcessor(),
        }
        self.tasks: List[asyncio.Task] = []
        self.is_running = False
    
    async def start(self):
        """Start all stage processors."""
        if self.is_running:
            logger.warning("Workflow engine already running")
            return
        
        self.is_running = True
        logger.info("Starting workflow engine")
        
        # Start all processors
        for stage, processor in self.processors.items():
            task = asyncio.create_task(processor.start())
            self.tasks.append(task)
            logger.info(f"Started processor for stage: {stage}")
    
    async def stop(self):
        """Stop all stage processors."""
        if not self.is_running:
            return
        
        self.is_running = False
        logger.info("Stopping workflow engine")
        
        # Stop all processors
        for processor in self.processors.values():
            await processor.stop()
        
        # Cancel all tasks
        for task in self.tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)
        
        self.tasks.clear()
        logger.info("Workflow engine stopped")
    
    def get_status(self) -> Dict:
        """Get status of all processors."""
        return {
            "engine_running": self.is_running,
            "processors": {
                stage.value: {
                    "status": processor.status.value,
                    "current_automation": processor.current_automation_id,
                    "poll_interval": processor.poll_interval
                }
                for stage, processor in self.processors.items()
            }
        }
    
    async def trigger_stage_check(self, stage: Stage):
        """
        Manually trigger a check for work in a specific stage.
        Useful for immediate processing without waiting for poll interval.
        """
        if stage in self.processors:
            processor = self.processors[stage]
            if processor.status == WorkerStatus.IDLE:
                await processor._process_next_item()


# Global workflow engine instance
workflow_engine = WorkflowEngine()
