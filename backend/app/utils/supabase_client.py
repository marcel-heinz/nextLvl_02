"""Supabase client for database operations"""
import os
from typing import List, Optional, Dict
from datetime import datetime
from uuid import uuid4

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("WARNING: Supabase library not installed. Using in-memory storage.")
    
from app.models.automation import Automation, AutomationCreate, AutomationUpdate, Stage


class SupabaseService:
    def __init__(self):
        # In-memory fallback storage
        self.memory_store: Dict[str, Automation] = {}
        
        # Get Supabase credentials from environment
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_TOKEN")
        
        if not SUPABASE_AVAILABLE:
            print("WARNING: Supabase library not available. Using in-memory storage.")
            self.client = None
            self.is_configured = False
        elif not self.supabase_url or not self.supabase_key:
            print("WARNING: Supabase not configured. Using in-memory storage.")
            self.client = None
            self.is_configured = False
        else:
            try:
                self.client: Client = create_client(self.supabase_url, self.supabase_key)
                self.is_configured = True
                self._ensure_table_exists()
            except Exception as e:
                print(f"ERROR: Failed to initialize Supabase client: {e}")
                print("Falling back to in-memory storage.")
                self.client = None
                self.is_configured = False
    
    def _ensure_table_exists(self):
        """Ensure the automations table exists with proper schema"""
        if not self.is_configured:
            return
            
        # The table creation should be done via Supabase dashboard or migrations
        # But we can check if table exists and create if needed
        try:
            # Test if table exists by trying to select from it
            result = self.client.table('automations').select('id').limit(1).execute()
            print("Automations table exists and is accessible")
        except Exception as e:
            print(f"Automations table might not exist or is not accessible: {e}")
            print("Please create the table manually in Supabase dashboard with the following schema:")
            print("""
            CREATE TABLE automations (
                id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                stage VARCHAR(50) NOT NULL DEFAULT 'New',
                file_name VARCHAR(255),
                file_url VARCHAR(1000),
                blob_name VARCHAR(255),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            """)
    
    async def create_automation(self, automation_data: AutomationCreate, automation_id: str = None) -> Optional[Automation]:
        """Create a new automation record"""
        if not self.is_configured:
            # Use in-memory storage as fallback
            new_id = automation_id or str(uuid4())
            now = datetime.utcnow()
            automation = Automation(
                id=new_id,
                title=automation_data.title,
                stage=automation_data.stage or Stage.NEW,
                file_name=automation_data.file_name,
                file_url=automation_data.file_url,
                blob_name=automation_data.blob_name,
                created_at=now,
                updated_at=now
            )
            self.memory_store[new_id] = automation
            print(f"Created automation {new_id} in memory storage")
            return automation
            
        try:
            now = datetime.utcnow().isoformat()
            data = {
                "title": automation_data.title,
                "stage": automation_data.stage or Stage.NEW,
                "file_name": automation_data.file_name,
                "file_url": automation_data.file_url,
                "blob_name": automation_data.blob_name,
                "created_at": now,
                "updated_at": now
            }
            
            if automation_id:
                data["id"] = automation_id
            
            result = self.client.table('automations').insert(data).execute()
            
            if result.data:
                automation_dict = result.data[0]
                return Automation(**automation_dict)
            return None
            
        except Exception as e:
            print(f"Failed to create automation in Supabase: {e}")
            return None
    
    async def get_automations(self) -> List[Automation]:
        """Get all automation records"""
        if not self.is_configured:
            # Return from in-memory storage
            automations = list(self.memory_store.values())
            # Sort by created_at descending
            automations.sort(key=lambda x: x.created_at, reverse=True)
            return automations
            
        try:
            result = self.client.table('automations').select('*').order('created_at', desc=True).execute()
            
            automations = []
            if result.data:
                for item in result.data:
                    try:
                        automation = Automation(**item)
                        automations.append(automation)
                    except Exception as e:
                        print(f"Failed to parse automation {item.get('id', 'unknown')}: {e}")
                        
            return automations
            
        except Exception as e:
            print(f"Failed to fetch automations from Supabase: {e}")
            return []
    
    async def get_automation(self, automation_id: str) -> Optional[Automation]:
        """Get a single automation by ID"""
        if not self.is_configured:
            # Return from in-memory storage
            return self.memory_store.get(automation_id)
            
        try:
            result = self.client.table('automations').select('*').eq('id', automation_id).execute()
            
            if result.data and len(result.data) > 0:
                return Automation(**result.data[0])
            return None
            
        except Exception as e:
            print(f"Failed to fetch automation {automation_id} from Supabase: {e}")
            return None
    
    async def update_automation(self, automation_id: str, update_data: AutomationUpdate) -> Optional[Automation]:
        """Update an automation record"""
        if not self.is_configured:
            # Update in-memory storage
            if automation_id not in self.memory_store:
                return None
            
            automation = self.memory_store[automation_id]
            
            # Update fields if provided
            if update_data.title is not None:
                automation.title = update_data.title
            if update_data.stage is not None:
                automation.stage = update_data.stage
            if update_data.file_name is not None:
                automation.file_name = update_data.file_name
            if update_data.file_url is not None:
                automation.file_url = update_data.file_url
            if update_data.blob_name is not None:
                automation.blob_name = update_data.blob_name
            
            automation.updated_at = datetime.utcnow()
            return automation
            
        try:
            data = {}
            
            # Only include fields that are set
            if update_data.title is not None:
                data["title"] = update_data.title
            if update_data.stage is not None:
                data["stage"] = update_data.stage
            if update_data.file_name is not None:
                data["file_name"] = update_data.file_name
            if update_data.file_url is not None:
                data["file_url"] = update_data.file_url
            if update_data.blob_name is not None:
                data["blob_name"] = update_data.blob_name
                
            data["updated_at"] = datetime.utcnow().isoformat()
            
            result = self.client.table('automations').update(data).eq('id', automation_id).execute()
            
            if result.data and len(result.data) > 0:
                return Automation(**result.data[0])
            return None
            
        except Exception as e:
            print(f"Failed to update automation {automation_id} in Supabase: {e}")
            return None
    
    async def delete_automation(self, automation_id: str) -> bool:
        """Delete an automation record"""
        if not self.is_configured:
            # Delete from in-memory storage
            if automation_id in self.memory_store:
                del self.memory_store[automation_id]
                return True
            return False
            
        try:
            result = self.client.table('automations').delete().eq('id', automation_id).execute()
            return True
            
        except Exception as e:
            print(f"Failed to delete automation {automation_id} from Supabase: {e}")
            return False
    
    async def get_automations_by_stage(self, stage: Stage, limit: int = None) -> List[Automation]:
        """Get automations filtered by stage, ordered by created_at ASC (oldest first for FIFO processing)"""
        if not self.is_configured:
            # Filter from in-memory storage
            automations = [auto for auto in self.memory_store.values() if auto.stage == stage]
            # Sort by created_at ascending (FIFO - oldest first)
            automations.sort(key=lambda x: x.created_at)
            if limit:
                automations = automations[:limit]
            return automations
            
        try:
            # Use the string value of the enum for database query
            stage_value = stage.value if hasattr(stage, 'value') else str(stage)
            query = self.client.table('automations').select('*').eq('stage', stage_value).order('created_at', desc=False)
            
            if limit:
                query = query.limit(limit)
                
            result = query.execute()
            
            automations = []
            if result.data:
                for item in result.data:
                    try:
                        automation = Automation(**item)
                        automations.append(automation)
                    except Exception as e:
                        print(f"Failed to parse automation {item.get('id', 'unknown')}: {e}")
                        
            return automations
            
        except Exception as e:
            print(f"Failed to fetch automations by stage {stage} from Supabase: {e}")
            return []
    
    async def get_latest_pipeline_config(self) -> Optional[Dict]:
        """Get the latest pipeline configuration"""
        if not self.is_configured:
            # Return None for in-memory mode
            return None
            
        try:
            result = self.client.table('pipeline_configs').select('*').order('version', desc=True).limit(1).execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]
            return None
            
        except Exception as e:
            print(f"Failed to fetch pipeline config from Supabase: {e}")
            return None
    
    async def update_automation_fields(self, automation_id: str, update_data: Dict) -> bool:
        """Update specific fields of an automation"""
        if not self.is_configured:
            # Update in-memory storage
            if automation_id in self.memory_store:
                automation = self.memory_store[automation_id]
                for key, value in update_data.items():
                    if hasattr(automation, key):
                        setattr(automation, key, value)
                automation.updated_at = datetime.now()
                return True
            return False
            
        try:
            result = self.client.table('automations').update(update_data).eq('id', automation_id).execute()
            return len(result.data) > 0
            
        except Exception as e:
            print(f"Failed to update automation fields {automation_id} in Supabase: {e}")
            return False
    
    async def create_pipeline_config(self, config_data: Dict) -> Optional[Dict]:
        """Create a new pipeline configuration"""
        if not self.is_configured:
            # For in-memory mode, just return the data with a fake ID
            config_data['id'] = str(uuid4())
            return config_data
            
        try:
            result = self.client.table('pipeline_configs').insert(config_data).execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]
            return None
            
        except Exception as e:
            print(f"Failed to create pipeline config in Supabase: {e}")
            return None
    
    async def get_pipeline_config_history(self, limit: int = 10) -> List[Dict]:
        """Get pipeline configuration history"""
        if not self.is_configured:
            # Return empty list for in-memory mode
            return []
            
        try:
            result = self.client.table('pipeline_configs').select('*').order('version', desc=True).limit(limit).execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            print(f"Failed to fetch pipeline config history from Supabase: {e}")
            return []
    
    async def delete_all_pipeline_configs(self) -> bool:
        """Delete all pipeline configurations"""
        if not self.is_configured:
            # For in-memory mode, always return True
            return True
            
        try:
            result = self.client.table('pipeline_configs').delete().neq('id', '').execute()
            return True
            
        except Exception as e:
            print(f"Failed to delete pipeline configs from Supabase: {e}")
            return False


# Singleton instance
supabase_service = SupabaseService()
