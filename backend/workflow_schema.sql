-- Enhanced Supabase schema for workflow management
-- Run this in your Supabase SQL editor to add workflow tracking capabilities

-- Add workflow tracking columns to existing automations table
ALTER TABLE automations ADD COLUMN IF NOT EXISTS processing_started_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE automations ADD COLUMN IF NOT EXISTS processing_completed_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE automations ADD COLUMN IF NOT EXISTS retry_count INTEGER DEFAULT 0;
ALTER TABLE automations ADD COLUMN IF NOT EXISTS last_error TEXT;
ALTER TABLE automations ADD COLUMN IF NOT EXISTS processing_metadata JSONB;
ALTER TABLE automations ADD COLUMN IF NOT EXISTS assigned_worker VARCHAR(100);

-- Add classification-specific fields to automations table
ALTER TABLE automations ADD COLUMN IF NOT EXISTS lob VARCHAR(255);
ALTER TABLE automations ADD COLUMN IF NOT EXISTS process VARCHAR(255);
ALTER TABLE automations ADD COLUMN IF NOT EXISTS classification_status VARCHAR(50) DEFAULT 'pending';
ALTER TABLE automations ADD COLUMN IF NOT EXISTS case_parameters JSONB;

-- Create indexes for workflow queries
CREATE INDEX IF NOT EXISTS idx_automations_stage_created_at ON automations(stage, created_at);
CREATE INDEX IF NOT EXISTS idx_automations_processing_started ON automations(processing_started_at) WHERE processing_started_at IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_automations_assigned_worker ON automations(assigned_worker) WHERE assigned_worker IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_automations_classification_status ON automations(classification_status);

-- Create workflow_events table for audit trail
CREATE TABLE IF NOT EXISTS workflow_events (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    automation_id UUID NOT NULL REFERENCES automations(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL, -- 'stage_changed', 'processing_started', 'processing_completed', 'error_occurred'
    from_stage VARCHAR(50),
    to_stage VARCHAR(50),
    worker_id VARCHAR(100),
    metadata JSONB,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for workflow events
CREATE INDEX IF NOT EXISTS idx_workflow_events_automation_id ON workflow_events(automation_id);
CREATE INDEX IF NOT EXISTS idx_workflow_events_created_at ON workflow_events(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_workflow_events_type ON workflow_events(event_type);

-- Create workflow_stats table for monitoring
CREATE TABLE IF NOT EXISTS workflow_stats (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    stage VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    items_processed INTEGER DEFAULT 0,
    avg_processing_time_seconds DECIMAL(10,2),
    success_count INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(stage, date)
);

-- Index for workflow stats
CREATE INDEX IF NOT EXISTS idx_workflow_stats_stage_date ON workflow_stats(stage, date);

-- Create pipeline_configs table for classification configuration
CREATE TABLE IF NOT EXISTS pipeline_configs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    lob_prompt TEXT NOT NULL,
    process_prompt TEXT NOT NULL,
    lob_process_pairs JSONB NOT NULL, -- array of {lob: str, process: str} objects
    llm_params JSONB NOT NULL, -- e.g., {temperature: float, max_tokens: int} for both Mistral and GPT
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for pipeline_configs
CREATE INDEX IF NOT EXISTS idx_pipeline_configs_version ON pipeline_configs(version DESC);

-- Function to log workflow events
CREATE OR REPLACE FUNCTION log_workflow_event(
    p_automation_id UUID,
    p_event_type VARCHAR(50),
    p_from_stage VARCHAR(50) DEFAULT NULL,
    p_to_stage VARCHAR(50) DEFAULT NULL,
    p_worker_id VARCHAR(100) DEFAULT NULL,
    p_metadata JSONB DEFAULT NULL,
    p_error_message TEXT DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    event_id UUID;
BEGIN
    INSERT INTO workflow_events (
        automation_id, 
        event_type, 
        from_stage, 
        to_stage, 
        worker_id, 
        metadata, 
        error_message
    ) VALUES (
        p_automation_id, 
        p_event_type, 
        p_from_stage, 
        p_to_stage, 
        p_worker_id, 
        p_metadata, 
        p_error_message
    ) RETURNING id INTO event_id;
    
    RETURN event_id;
END;
$$ LANGUAGE plpgsql;

-- Function to track stage changes and log events
CREATE OR REPLACE FUNCTION track_stage_changes()
RETURNS TRIGGER AS $$
BEGIN
    -- Log stage change event if stage was updated
    IF OLD.stage IS DISTINCT FROM NEW.stage THEN
        PERFORM log_workflow_event(
            NEW.id,
            'stage_changed',
            OLD.stage,
            NEW.stage,
            NEW.assigned_worker,
            jsonb_build_object(
                'previous_updated_at', OLD.updated_at,
                'new_updated_at', NEW.updated_at
            )
        );
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for stage change tracking
DROP TRIGGER IF EXISTS trigger_track_stage_changes ON automations;
CREATE TRIGGER trigger_track_stage_changes
    AFTER UPDATE ON automations
    FOR EACH ROW
    EXECUTE FUNCTION track_stage_changes();

-- Function to update workflow statistics
CREATE OR REPLACE FUNCTION update_workflow_stats(
    p_stage VARCHAR(50),
    p_processing_time_seconds DECIMAL DEFAULT NULL,
    p_success BOOLEAN DEFAULT TRUE
)
RETURNS VOID AS $$
DECLARE
    today DATE := CURRENT_DATE;
    current_stats RECORD;
BEGIN
    -- Get current stats for today
    SELECT * INTO current_stats 
    FROM workflow_stats 
    WHERE stage = p_stage AND date = today;
    
    IF FOUND THEN
        -- Update existing stats
        UPDATE workflow_stats SET
            items_processed = items_processed + 1,
            success_count = success_count + CASE WHEN p_success THEN 1 ELSE 0 END,
            error_count = error_count + CASE WHEN p_success THEN 0 ELSE 1 END,
            avg_processing_time_seconds = CASE 
                WHEN p_processing_time_seconds IS NOT NULL THEN
                    ((avg_processing_time_seconds * (items_processed - 1)) + p_processing_time_seconds) / items_processed
                ELSE avg_processing_time_seconds
            END,
            updated_at = NOW()
        WHERE stage = p_stage AND date = today;
    ELSE
        -- Insert new stats
        INSERT INTO workflow_stats (
            stage, 
            date, 
            items_processed, 
            success_count, 
            error_count, 
            avg_processing_time_seconds
        ) VALUES (
            p_stage,
            today,
            1,
            CASE WHEN p_success THEN 1 ELSE 0 END,
            CASE WHEN p_success THEN 0 ELSE 1 END,
            p_processing_time_seconds
        );
    END IF;
END;
$$ LANGUAGE plpgsql;

-- View for workflow overview
CREATE OR REPLACE VIEW workflow_overview AS
SELECT 
    stage,
    COUNT(*) as total_items,
    COUNT(CASE WHEN processing_started_at IS NOT NULL AND processing_completed_at IS NULL THEN 1 END) as currently_processing,
    COUNT(CASE WHEN retry_count > 0 THEN 1 END) as items_with_retries,
    AVG(CASE 
        WHEN processing_started_at IS NOT NULL AND processing_completed_at IS NOT NULL 
        THEN EXTRACT(EPOCH FROM (processing_completed_at - processing_started_at)) 
    END) as avg_processing_time_seconds,
    MIN(created_at) as oldest_item,
    MAX(created_at) as newest_item
FROM automations 
GROUP BY stage
ORDER BY 
    CASE stage 
        WHEN 'New' THEN 1 
        WHEN 'Classification' THEN 2 
        WHEN 'Data Extraction' THEN 3 
        WHEN 'Processing' THEN 4 
        WHEN 'Done' THEN 5 
        ELSE 6 
    END;

-- View for recent workflow activity
CREATE OR REPLACE VIEW recent_workflow_activity AS
SELECT 
    we.created_at,
    we.event_type,
    we.from_stage,
    we.to_stage,
    we.worker_id,
    a.title as automation_title,
    a.id as automation_id,
    we.error_message
FROM workflow_events we
JOIN automations a ON we.automation_id = a.id
ORDER BY we.created_at DESC
LIMIT 100;

-- Grant permissions (adjust as needed for your setup)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON automations TO authenticated;
-- GRANT SELECT, INSERT ON workflow_events TO authenticated;
-- GRANT SELECT ON workflow_stats TO authenticated;
-- GRANT SELECT ON workflow_overview TO authenticated;
-- GRANT SELECT ON recent_workflow_activity TO authenticated;
