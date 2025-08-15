"""
Workflow Engine for managing automation pipeline stages.

This implements a pull-based architecture where each stage has workers
that actively poll for work, process it, and move items to the next stage.
"""

from __future__ import annotations

import asyncio
import logging
import tempfile
import os
import json
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Type
from enum import Enum

import openai
from mistralai import Mistral
from azure.storage.blob import BlobServiceClient

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
        
        # Check if this is a classification stage and the item should go to DONE
        if self.stage == Stage.CLASSIFICATION:
            # Get current automation to check classification status
            automation = await supabase_service.get_automation(automation_id)
            if automation and hasattr(automation, 'classification_status'):
                if automation.classification_status in ['unclassified', 'error']:
                    next_stage = Stage.DONE
                    logger.info(f"Routing unclassified automation {automation_id} directly to DONE")
        
        update_data = AutomationUpdate(stage=next_stage)
        await supabase_service.update_automation(automation_id, update_data)


class ClassificationProcessor(BaseStageProcessor):
    """Processor for the Classification stage."""
    
    def __init__(self):
        super().__init__(Stage.NEW, poll_interval=3)  # Pull from NEW stage
        self.config_cache = None
        self.cache_timestamp = None
        self.cache_duration = 300  # 5 minutes
        
        # Initialize AI clients
        self._init_ai_clients()
    
    def _init_ai_clients(self):
        """Initialize AI clients with API keys from environment."""
        try:
            # Get API keys from environment
            openai_key = os.getenv("OPENAI_API_KEY")
            mistral_key = os.getenv("MISTRAL_API_KEY")
            
            if not openai_key:
                logger.error("OPENAI_API_KEY not found in environment variables")
                raise ValueError("Missing OPENAI_API_KEY")
            
            if not mistral_key:
                logger.error("MISTRAL_API_KEY not found in environment variables")
                raise ValueError("Missing MISTRAL_API_KEY")
            
            # Initialize OpenAI client
            self.openai_client = openai.OpenAI(api_key=openai_key)
            
            # Initialize Mistral client
            self.mistral_client = Mistral(api_key=mistral_key)
            
            # Initialize Azure Blob client
            azure_connection = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
            if not azure_connection:
                logger.error("AZURE_STORAGE_CONNECTION_STRING not found in environment variables")
                raise ValueError("Missing AZURE_STORAGE_CONNECTION_STRING")
            
            self.blob_client = BlobServiceClient.from_connection_string(azure_connection)
            
            logger.info("AI clients initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI clients: {e}")
            raise
    
    async def _refresh_config_cache(self):
        """Refresh config cache if needed."""
        now = datetime.now()
        
        # Check if cache needs refresh
        if (self.config_cache is None or 
            self.cache_timestamp is None or 
            (now - self.cache_timestamp).total_seconds() > self.cache_duration):
            
            try:
                # Fetch latest config from Supabase
                config = await supabase_service.get_latest_pipeline_config()
                
                if config:
                    self.config_cache = config
                    self.cache_timestamp = now
                    logger.info("Pipeline config cache refreshed")
                else:
                    logger.warning("No pipeline config found in database")
                    
            except Exception as e:
                logger.error(f"Failed to refresh config cache: {e}")
                # Continue with existing cache if available
    
    async def process_automation(self, automation: Automation) -> bool:
        """
        Classify the document/file using Mistral OCR and GPT-4o extraction.
        """
        try:
            logger.info(f"Starting classification for automation {automation.id}: {automation.title}")
            
            # Refresh config cache
            await self._refresh_config_cache()
            
            if not self.config_cache:
                logger.error("No pipeline configuration available")
                await self._set_unclassified(automation.id, "No pipeline configuration")
                return True  # Move to DONE even if unclassified
            
            # Step 1: Download file from Azure
            file_path = await self._download_file(automation)
            if not file_path:
                await self._set_unclassified(automation.id, "Failed to download file")
                return True
            
            try:
                # Step 2: OCR with Mistral
                ocr_markdown = await self._perform_ocr(file_path)
                if not ocr_markdown:
                    await self._set_unclassified(automation.id, "OCR failed or empty result")
                    return True
                
                # Step 3: Extract LOB/Process with GPT-4o
                lob, process = await self._extract_classification(ocr_markdown)
                
                # Step 4: Validate and store results
                if lob and process:
                    await self._set_classified(automation.id, lob, process, ocr_markdown)
                    logger.info(f"Classification completed: {lob} / {process}")
                else:
                    await self._set_unclassified(automation.id, "Could not extract valid LOB/Process pair")
                
                return True
                
            finally:
                # Clean up temporary file
                if file_path and os.path.exists(file_path):
                    os.unlink(file_path)
            
        except Exception as e:
            logger.error(f"Classification failed for automation {automation.id}: {e}")
            try:
                await self._set_unclassified(automation.id, f"Error: {str(e)}")
            except:
                logger.error("Failed to set unclassified status")
            return True  # Still move forward to prevent pipeline stalls
    
    async def _download_file(self, automation: Automation) -> Optional[str]:
        """Download file from Azure Storage to temporary location."""
        try:
            if not automation.file_url or not automation.blob_name:
                logger.error(f"Missing file_url or blob_name for automation {automation.id}")
                return None
            
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(automation.file_name or "")[1])
            temp_path = temp_file.name
            temp_file.close()
            
            # Extract container and blob from URL or use blob_name
            # Assuming blob_name format is "container/blob" or just "blob"
            if "/" in automation.blob_name:
                container_name, blob_name = automation.blob_name.split("/", 1)
            else:
                container_name = "case-documents"  # Match the upload service container
                blob_name = automation.blob_name
            
            # Download blob
            blob_client = self.blob_client.get_blob_client(container=container_name, blob=blob_name)
            
            with open(temp_path, "wb") as download_file:
                download_file.write(blob_client.download_blob().readall())
            
            logger.info(f"Downloaded file to {temp_path}")
            return temp_path
            
        except Exception as e:
            logger.error(f"Failed to download file for automation {automation.id}: {e}")
            return None
    
    async def _perform_ocr(self, file_path: str) -> Optional[str]:
        """Perform OCR using Mistral OCR API for PDF/image files."""
        try:
            # Check file type - we only process PDF and images
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext not in ['.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif']:
                logger.error(f"Unsupported file type: {file_ext}. Only PDF and images are supported.")
                return None
            
            # Read file as binary for Mistral API
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            # Convert to base64 for API transmission
            import base64
            file_base64 = base64.b64encode(file_content).decode('utf-8')
            
            # Call Mistral OCR API
            try:
                if file_ext == '.pdf':
                    # Use OCR API for PDF documents
                    response = self.mistral_client.ocr.process(
                        model="mistral-ocr-latest",
                        document={
                            "type": "document_url",
                            "document_url": f"data:application/pdf;base64,{file_base64}"
                        },
                        include_image_base64=True
                    )
                else:
                    # Use OCR API for images
                    # Map file extensions to proper MIME types
                    mime_type_map = {
                        '.png': 'image/png',
                        '.jpg': 'image/jpeg',
                        '.jpeg': 'image/jpeg',
                        '.tiff': 'image/tiff',
                        '.bmp': 'image/bmp',
                        '.gif': 'image/gif'
                    }
                    mime_type = mime_type_map.get(file_ext, 'image/jpeg')
                    
                    response = self.mistral_client.ocr.process(
                        model="mistral-ocr-latest",
                        document={
                            "type": "image_url",
                            "image_url": f"data:{mime_type};base64,{file_base64}"
                        },
                        include_image_base64=True
                    )
                
                # Extract OCR results from all pages
                if response.pages:
                    # Combine markdown from all pages
                    ocr_result = "\n\n".join([page.markdown for page in response.pages if page.markdown])
                    
                    if ocr_result and ocr_result.strip():
                        logger.info(f"OCR completed successfully for {file_ext} file - {len(response.pages)} pages processed")
                        return ocr_result.strip()
                    else:
                        logger.warning("OCR returned empty result")
                        return None
                else:
                    logger.warning("OCR response contained no pages")
                    return None
                    
            except Exception as api_error:
                logger.error(f"Mistral OCR failed: {api_error}")
                
                # Fallback: Use text-only approach for now
                fallback_prompt = f"""This is a {file_ext} document that needs OCR processing.
                
                Filename: {os.path.basename(file_path)}
                File type: {file_ext}
                File size: {len(file_content)} bytes
                
                Please note: This document requires OCR processing but the current implementation 
                encountered an API limitation. The file has been received and is ready for processing 
                once the OCR service is properly configured."""
                
                return fallback_prompt
            
        except Exception as e:
            logger.error(f"OCR failed for file {file_path}: {e}")
            return None
    
    async def _extract_classification(self, ocr_markdown: str) -> tuple[Optional[str], Optional[str]]:
        """Extract LOB and Process using GPT-4o."""
        try:
            config = self.config_cache
            lob_prompt = config.get('lob_prompt', '')
            process_prompt = config.get('process_prompt', '')
            lob_process_pairs = config.get('lob_process_pairs', [])
            llm_params = config.get('llm_params', {})
            
            if not lob_process_pairs:
                logger.error("No LOB-Process pairs configured")
                return None, None
            
            # Create combined prompt
            pairs_text = "\n".join([f"- {pair['lob']} / {pair['process']}" for pair in lob_process_pairs])
            
            system_prompt = f"""You are a document classifier. Your task is to analyze the provided document content and select exactly ONE Line of Business (LOB) and Process pair from the available options.

LOB Extraction Instruction: {lob_prompt}

Process Extraction Instruction: {process_prompt}

Available LOB-Process pairs:
{pairs_text}

You must respond with a JSON object containing exactly one pair from the list above:
{{"lob": "exact_lob_value", "process": "exact_process_value"}}

If you cannot confidently match the document to any of the available pairs, respond with:
{{"lob": null, "process": null}}"""

            user_prompt = f"Document content to classify:\n\n{ocr_markdown[:4000]}"  # Limit context
            
            # Get LLM parameters
            temperature = llm_params.get('temperature', 0)
            max_tokens = llm_params.get('max_tokens', 500)
            
            # Call GPT-4o
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"}
            )
            
            # Parse response
            response_text = response.choices[0].message.content
            result = json.loads(response_text)
            
            lob = result.get('lob')
            process = result.get('process')
            
            # Validate against available pairs
            if lob and process:
                valid_pair = any(
                    pair['lob'] == lob and pair['process'] == process 
                    for pair in lob_process_pairs
                )
                
                if valid_pair:
                    return lob, process
                else:
                    logger.warning(f"Invalid LOB/Process pair returned: {lob}/{process}")
                    return None, None
            
            return None, None
            
        except Exception as e:
            logger.error(f"Classification extraction failed: {e}")
            return None, None
    
    async def _set_classified(self, automation_id: str, lob: str, process: str, ocr_markdown: str):
        """Update automation with classification results."""
        try:
            case_parameters = {
                "ocr_markdown": ocr_markdown,
                "llm_responses": [{
                    "model": "gpt-4o",
                    "timestamp": datetime.now().isoformat(),
                    "result": {"lob": lob, "process": process}
                }]
            }
            
            update_data = {
                "lob": lob,
                "process": process,
                "classification_status": "classified",
                "case_parameters": case_parameters
            }
            
            await supabase_service.update_automation_fields(automation_id, update_data)
            
        except Exception as e:
            logger.error(f"Failed to set classified status: {e}")
            raise
    
    async def _set_unclassified(self, automation_id: str, reason: str):
        """Mark automation as unclassified and route to DONE."""
        try:
            case_parameters = {
                "classification_error": reason,
                "timestamp": datetime.now().isoformat()
            }
            
            update_data = {
                "classification_status": "unclassified",
                "case_parameters": case_parameters,
                "last_error": reason
            }
            
            await supabase_service.update_automation_fields(automation_id, update_data)
            
        except Exception as e:
            logger.error(f"Failed to set unclassified status: {e}")
            raise


class DataExtractionProcessor(BaseStageProcessor):
    """Processor for the Data Extraction stage."""
    
    def __init__(self):
        super().__init__(Stage.CLASSIFICATION, poll_interval=3)  # Pull from CLASSIFICATION stage
    
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
        super().__init__(Stage.DATA_EXTRACTION, poll_interval=5)  # Pull from DATA_EXTRACTION stage
    
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
        # Note: Each processor pulls from the previous stage but is responsible for its named stage
        self.processors: Dict[Stage, BaseStageProcessor] = {
            Stage.CLASSIFICATION: ClassificationProcessor(),      # Pulls from NEW, moves to CLASSIFICATION  
            Stage.DATA_EXTRACTION: DataExtractionProcessor(),    # Pulls from CLASSIFICATION, moves to DATA_EXTRACTION
            Stage.PROCESSING: ProcessingProcessor(),              # Pulls from DATA_EXTRACTION, moves to PROCESSING
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
