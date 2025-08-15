-- Supabase table schema for automations
-- Run this in your Supabase SQL editor to create the table

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

-- Create index for better performance
CREATE INDEX idx_automations_created_at ON automations(created_at DESC);
CREATE INDEX idx_automations_stage ON automations(stage);

-- Enable Row Level Security (optional, for future multi-tenant support)
ALTER TABLE automations ENABLE ROW LEVEL SECURITY;

-- Create a policy to allow all operations for now (modify as needed)
CREATE POLICY "Allow all operations on automations" ON automations
    FOR ALL USING (true) WITH CHECK (true);

-- Create a function to automatically update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_automations_updated_at 
    BEFORE UPDATE ON automations 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();
