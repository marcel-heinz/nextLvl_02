# Workflow Engine Guide

## Overview

The nxtLvl application now includes a robust, scalable workflow engine that automatically processes automations through different stages of your pipeline. This guide explains how the system works and how to use it.

## Architecture: Pull-Based Workflow System

We've implemented a **pull-based architecture** which offers several advantages:

### Why Pull-Based?

1. **Natural Backpressure**: Services only process what they can handle
2. **Resilient**: If a service is down, work accumulates safely in the database
3. **Scalable**: Easy to scale individual stages independently
4. **Simple**: Easier to debug and maintain than event-driven systems
5. **Cost-effective**: Can run fewer workers during low-load periods

### How It Works

```
[NEW] → [CLASSIFICATION] → [DATA EXTRACTION] → [PROCESSING] → [DONE]
   ↓           ↓                    ↓               ↓           
Worker 1    Worker 2           Worker 3        Worker 4
(polls)     (polls)            (polls)         (polls)
```

Each stage has dedicated worker processes that:
- Poll the database for work in their assigned stage
- Process items one at a time
- Move completed items to the next stage
- Handle errors gracefully with retry logic

## Workflow Stages

1. **NEW**: Items uploaded and ready for classification
2. **CLASSIFICATION**: AI classification of document type/content
3. **DATA EXTRACTION**: Extract structured data from classified documents
4. **PROCESSING**: Final processing and business rule application
5. **DONE**: Completed items ready for export/usage

## Getting Started

### 1. Database Setup

First, apply the enhanced database schema:

```sql
-- Run this in your Supabase SQL editor
-- Content from backend/workflow_schema.sql
```

This adds:
- Workflow tracking columns to automations table
- workflow_events table for audit trail
- workflow_stats table for monitoring
- Database functions for logging and statistics
- Views for easy monitoring

### 2. Start the API Server

The workflow engine automatically starts with the FastAPI application:

```bash
cd backend
python app/main.py
```

The workflow engine will start automatically and begin processing items.

### 3. Monitor the Workflow

#### Health Check
```bash
curl http://localhost:8000/api/health
```

#### Workflow Status
```bash
curl http://localhost:8000/api/workflow/status
```

#### Workflow Metrics
```bash
curl http://localhost:8000/api/workflow/metrics
```

## API Endpoints

### Workflow Management

- `GET /api/workflow/status` - Get engine and processor status
- `POST /api/workflow/start` - Start the workflow engine
- `POST /api/workflow/stop` - Stop the workflow engine
- `POST /api/workflow/restart` - Restart the workflow engine

### Manual Controls

- `POST /api/workflow/trigger-stage` - Manually trigger processing for a stage
- `POST /api/workflow/move-to-next-stage/{automation_id}` - Manually move item to next stage

### Monitoring

- `GET /api/workflow/metrics` - Get queue lengths and processor status
- `GET /api/workflow/stages` - Get stage information and flow

## How Items Move Through the Pipeline

### Automatic Flow

1. **Upload**: User uploads file → creates automation in "NEW" stage
2. **Auto-trigger**: Upload endpoint automatically triggers Classification stage check
3. **Classification**: Worker picks up item, classifies it, moves to "Data Extraction"
4. **Data Extraction**: Worker extracts data, moves to "Processing"
5. **Processing**: Worker applies business rules, moves to "Done"

### Timing

- Each processor polls every 3-5 seconds (configurable)
- Processing is FIFO (First In, First Out) based on creation time
- Immediate trigger when new items are uploaded

## Customizing Processors

Each stage has its own processor class that you can customize:

### Classification Processor

```python
# In app/services/workflow_engine.py
class ClassificationProcessor(BaseStageProcessor):
    async def process_automation(self, automation: Automation) -> bool:
        # Your classification logic here
        # 1. Download file from automation.file_url
        # 2. Send to AI classification service
        # 3. Store results
        return True  # or False if failed
```

### Adding Your Own Logic

1. Download file from Azure Storage using `automation.file_url`
2. Call your AI/ML services
3. Store results (consider adding fields to the automation model)
4. Return `True` for success, `False` for failure

## Error Handling

The system includes robust error handling:

- **Processor Errors**: Failed items stay in current stage for retry
- **Backpressure**: Slow stages naturally throttle upstream processing
- **Service Failures**: If a processor crashes, items accumulate safely
- **Monitoring**: All events are logged to workflow_events table

## Configuration

### Poll Intervals

```python
# Customize in workflow_engine.py
ClassificationProcessor(poll_interval=3)     # 3 seconds
DataExtractionProcessor(poll_interval=3)     # 3 seconds  
ProcessingProcessor(poll_interval=5)         # 5 seconds
```

### Worker Scaling

To scale a specific stage, you can:
1. Decrease poll interval for faster processing
2. Run multiple instances (future enhancement)
3. Optimize the processing logic

## Monitoring and Debugging

### Database Views

The schema includes helpful views:

```sql
-- See queue lengths and processing times
SELECT * FROM workflow_overview;

-- See recent activity
SELECT * FROM recent_workflow_activity;

-- See daily statistics
SELECT * FROM workflow_stats WHERE date = CURRENT_DATE;
```

### Logs

The workflow engine logs all activities. Check your application logs for:
- Processing start/completion
- Errors and retries
- Stage transitions

### Manual Intervention

If items get stuck:

```bash
# Trigger immediate processing
curl -X POST http://localhost:8000/api/workflow/trigger-stage \
  -H "Content-Type: application/json" \
  -d '{"stage": "Classification"}'

# Manually move specific item
curl -X POST http://localhost:8000/api/workflow/move-to-next-stage/AUTOMATION_ID
```

## Performance Optimization

### For High Volume

1. **Tune Poll Intervals**: Decrease for faster processing
2. **Batch Processing**: Modify processors to handle multiple items
3. **Parallel Workers**: Implement multiple worker instances per stage
4. **Resource Scaling**: Scale compute resources for heavy processing stages

### For Low Volume

1. **Increase Poll Intervals**: Reduce resource usage
2. **Conditional Start**: Only start workflow when needed
3. **Sleep Mode**: Pause workflow during off-hours

## Future Enhancements

The current system provides a solid foundation for:

1. **Horizontal Scaling**: Multiple worker instances per stage
2. **Event Notifications**: Optional push notifications for immediate processing
3. **Priority Queues**: Process high-priority items first
4. **Workflow Visualization**: Real-time dashboard
5. **Advanced Retry Logic**: Exponential backoff, dead letter queues
6. **Multi-tenant Support**: Separate workflows per customer

## Troubleshooting

### Workflow Not Starting

1. Check logs during application startup
2. Verify database connectivity
3. Check `/api/health` endpoint

### Items Not Moving

1. Check `/api/workflow/status` for processor status
2. Look for errors in application logs
3. Check database for stuck items
4. Manually trigger processing

### Performance Issues

1. Monitor queue lengths via `/api/workflow/metrics`
2. Check processing times in workflow_stats table
3. Identify bottleneck stages
4. Optimize slow processors

## Example Usage

```python
# Upload a file (automatic workflow trigger)
files = {'file': open('document.pdf', 'rb')}
response = requests.post('http://localhost:8000/api/automations/upload', files=files)

# Monitor progress
automation_id = response.json()['id']
status = requests.get(f'http://localhost:8000/api/automations/{automation_id}')
print(f"Current stage: {status.json()['stage']}")

# Check overall workflow health
health = requests.get('http://localhost:8000/api/workflow/metrics')
print(f"Queue lengths: {health.json()['queue_lengths']}")
```

This workflow system provides a robust foundation for your automation pipeline that can scale from small workloads to enterprise-level processing volumes.
