# FastAPI Backend

Backend API server built with FastAPI and Python.

Implements an MVP `Automations` resource with in-memory CRUD and seed data.

## Setup

1. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # macOS/Linux
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup environment:**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

4. **Run development server:**
   ```bash
   python app/main.py
   # or
   uvicorn app.main:app --reload
   ```

## API Documentation

- Interactive docs: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

## Endpoints

- `GET /api/automations/` — list
- `POST /api/automations/` — create
- `GET /api/automations/{id}` — retrieve
- `PATCH /api/automations/{id}` — update
- `DELETE /api/automations/{id}` — delete

## Project Structure

```
app/
├── __init__.py
├── main.py          # FastAPI app and configuration
├── models/          # Pydantic models
├── routes/          # API route handlers
└── utils/           # Utility functions
```

## Development

Always activate the virtual environment before working:
```bash
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
```

When adding new dependencies:
```bash
pip install package-name
pip freeze > requirements.txt
```
