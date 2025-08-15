"""Azure Blob Storage service for file uploads"""
import os
from typing import Optional, Tuple
from uuid import uuid4

try:
    from azure.storage.blob import BlobServiceClient, ContentSettings, PublicAccess
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
    print("WARNING: Azure Storage library not installed. Using simulated storage.")

from fastapi import HTTPException, UploadFile


class AzureStorageService:
    def __init__(self):
        # Get connection string from environment
        self.connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        self.is_configured = bool(self.connection_string and AZURE_AVAILABLE)
        
        if not AZURE_AVAILABLE:
            print("WARNING: Azure Storage library not available. Using simulated storage.")
            self.container_name = "case-documents"
            self.blob_service_client = None
        elif self.is_configured:
            self.container_name = "case-documents"
            self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
            
            # Ensure container exists
            self._ensure_container_exists()
        else:
            print("WARNING: Azure Storage not configured. Files will be simulated (not actually stored).")
            self.container_name = "case-documents"
            self.blob_service_client = None
    
    def _ensure_container_exists(self):
        """Create the container if it doesn't exist"""
        if not self.is_configured:
            return
            
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            container_client.get_container_properties()
        except Exception:
            # Container doesn't exist, create it
            try:
                if AZURE_AVAILABLE:
                    self.blob_service_client.create_container(
                        self.container_name,
                        public_access=PublicAccess.Blob  # Allow public read access to blobs
                    )
                    print(f"Created container '{self.container_name}' with public blob access")
            except Exception as e:
                print(f"Warning: Could not create container: {e}")
    
    async def upload_file(self, file: UploadFile) -> Tuple[str, str]:
        """
        Upload a file to Azure Blob Storage (or simulate if not configured)
        
        Returns:
            Tuple of (blob_name, blob_url)
        """
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Generate unique blob name to avoid conflicts
        file_extension = os.path.splitext(file.filename)[1]
        blob_name = f"{uuid4()}{file_extension}"
        
        if not self.is_configured:
            # Development mode: simulate file upload
            await file.read()  # Read the file to simulate processing
            await file.seek(0)  # Reset file pointer
            
            # Return simulated values
            blob_url = f"https://localhost:8000/files/{blob_name}"
            print(f"SIMULATED: File '{file.filename}' would be uploaded as '{blob_name}'")
            return blob_name, blob_url
        
        try:
            # Read file content
            content = await file.read()
            
            # Reset file pointer for potential re-reading
            await file.seek(0)
            
            if self.is_configured and AZURE_AVAILABLE:
                # Upload to Azure Blob Storage
                blob_client = self.blob_service_client.get_blob_client(
                    container=self.container_name, 
                    blob=blob_name
                )
                
                blob_client.upload_blob(
                    content, 
                    overwrite=True,
                    content_settings=ContentSettings(content_type=file.content_type)
                )
                
                # Get the blob URL
                blob_url = blob_client.url
            else:
                # Simulated upload - just return fake URL
                blob_url = f"https://localhost:8000/files/{blob_name}"
                print(f"SIMULATED: File '{file.filename}' uploaded as '{blob_name}'")
            
            return blob_name, blob_url
            
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to upload file to Azure Storage: {str(e)}"
            )
    
    def delete_file(self, blob_name: str) -> bool:
        """
        Delete a file from Azure Blob Storage (or simulate if not configured)
        
        Returns:
            True if deleted successfully, False otherwise
        """
        if not self.is_configured:
            print(f"SIMULATED: File '{blob_name}' would be deleted")
            return True
            
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, 
                blob=blob_name
            )
            blob_client.delete_blob()
            return True
        except Exception as e:
            print(f"Failed to delete blob {blob_name}: {e}")
            return False
    
    def get_file_url(self, blob_name: str) -> Optional[str]:
        """Get the URL for a blob (or simulate if not configured)"""
        if not self.is_configured:
            return f"https://localhost:8000/files/{blob_name}"
            
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, 
                blob=blob_name
            )
            return blob_client.url
        except Exception:
            return None


# Singleton instance
azure_storage = AzureStorageService()
