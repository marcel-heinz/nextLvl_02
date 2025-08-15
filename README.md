# nxtLvl - Next.js + FastAPI Full Stack Application

A modern full-stack web application built with Next.js (TypeScript + Tailwind CSS) frontend and FastAPI (Python) backend, featuring an automated workflow engine for document processing.

## 🏗️ Project Structure

```
nxtLvl/
├── frontend/                 # Next.js frontend
│   ├── src/
│   │   ├── app/             # App Router pages including workflow-monitor
│   │   ├── components/      # Reusable components for pipeline and workflow
│   │   └── lib/            # Utility functions
│   ├── public/             # Static assets
│   ├── package.json        # Node.js dependencies
│   └── tailwind.config.js  # Tailwind configuration
├── backend/                 # FastAPI backend
│   ├── venv/               # Python virtual environment (not in git)
│   ├── app/
│   │   ├── main.py         # FastAPI app entry point with workflow lifecycle
│   │   ├── models/         # Pydantic models
│   │   ├── routes/         # API routes including workflow controls
│   │   ├── services/       # Services including workflow_engine.py
│   │   └── utils/          # Utilities for Supabase and Azure
│   ├── requirements.txt    # Python dependencies
│   ├── start_server.py     # Server startup script
│   ├── run.bat             # Windows batch file to start server
│   ├── env.example         # Environment variables template
│   ├── workflow_schema.sql # Supabase schema for workflow
│   └── WORKFLOW_GUIDE.md   # Detailed workflow documentation
└── README.md               # This file
```

## 🚀 Quick Start

### Prerequisites

- **Node.js** (v18+)
- **Python** (v3.11+)
- **npm** or **yarn**
- **Supabase Account** for database
- **Azure Storage Account** for file uploads

### 1. Clone and Setup

```bash
git clone https://github.com/marcel-heinz/nextLvl_02.git
cd nxtLvl
```

### 2. Database Setup (Supabase)

Create a Supabase project and run the schema:

1. Copy `backend/workflow_schema.sql` to your Supabase SQL editor and execute it.
2. Update `.env` with your Supabase URL and key (see env.example).

### 3. Backend Setup (FastAPI)

#### Using the startup script (Recommended)

```bash
# Navigate to backend
cd backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Copy env.example to .env and fill in values
cp env.example .env

# Run the server (handles all imports automatically)
python start_server.py
```

The API will be available at: `http://localhost:8001`
- API docs: `http://localhost:8001/docs`
- Health check: `http://localhost:8001/api/health`
- Automations: `http://localhost:8001/api/automations/`
- Workflow status: `http://localhost:8001/api/workflow/status`

### 3. Frontend Setup (Next.js)

```bash
# Navigate to frontend (new terminal)
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

The frontend will be available at: `http://localhost:3000`

## 🛠️ Development

### Backend Development

The backend uses port 8001 to avoid Windows permission issues.

```bash
# Always activate venv first
cd backend
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Easy startup
python start_server.py

# Or manual uvicorn
$env:PYTHONPATH="."  # Windows PowerShell
export PYTHONPATH="."  # macOS/Linux
uvicorn app.main:app --reload --port 8001
```

### Frontend Development

```bash
cd frontend

# Development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Linting
npm run lint
```

### Adding New Dependencies

#### Backend (Python)
```bash
# Activate venv first
venv\Scripts\activate

# Install new package
pip install package-name

# Update requirements.txt
pip freeze > requirements.txt
```

#### Frontend (Node.js)
```bash
cd frontend

# Install new package
npm install package-name

# Install dev dependency
npm install -D package-name
```

## 📁 Key Files

### Backend
- `backend/start_server.py` - Easy server startup script (recommended)
- `backend/run.bat` - Windows batch file for easy startup
- `backend/app/main.py` - FastAPI application entry point
- `backend/requirements.txt` - Python dependencies
- `backend/env.example` - Environment variables template

### Frontend
- `frontend/src/app/(app)/page.tsx` - Dashboard page
- `frontend/src/app/(app)/pipeline/page.tsx` - Main Kanban pipeline
- `frontend/package.json` - Node.js dependencies
- `frontend/next.config.ts` - API proxy configuration (points to port 8003)

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
ENVIRONMENT=development
API_HOST=127.0.0.1
API_PORT=8003
```

### CORS Configuration

The backend is configured to allow requests from `http://localhost:3000` (Next.js dev server). Update the CORS settings in `backend/app/main.py` for production.

### Port Configuration

- Backend: `http://localhost:8001` (changed to avoid Windows permission issues)
- Frontend: `http://localhost:3000`
- API proxy: Frontend proxies `/api/*` to backend automatically (see frontend/next.config.ts)

## 📦 Tech Stack

### Frontend
- **Framework**: Next.js 14+
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Components**: Custom UI library with teal theme
- **Architecture**: App Router with route groups

### Backend
- **Framework**: FastAPI 0.100+
- **Language**: Python 3.11+
- **Server**: Uvicorn
- **Validation**: Pydantic
- **Environment**: python-dotenv
- **Database**: Supabase (PostgreSQL)
- **Storage**: Azure Blob Storage
- **Workflow**: Asyncio-based pull workers

## 🏢 Application Features

### Core Features
- **Dashboard**: Overview of all modules
- **Automation Pipeline**: Kanban-style workflow with 5 stages (New, Classification, Data Extraction, Processing, Done)
- **Workflow Engine**: Automated pull-based processing with dedicated workers per stage
- **Workflow Monitor**: Real-time dashboard for engine status, metrics, and visualization
- **File Uploads**: Direct to Azure Blob Storage with Supabase tracking
- **CRUD Operations**: For automations with automatic workflow triggering

### Backend API
- **GET /api/automations/**: List all automations
- **POST /api/automations/upload**: Upload file to Azure and create automation in Supabase
- **PATCH /api/automations/{id}**: Update automation
- **DELETE /api/automations/{id}**: Delete automation
- **GET /api/workflow/status**: Workflow engine status
- **GET /api/workflow/metrics**: Queue lengths and stats
- **POST /api/workflow/start|stop|restart**: Control workflow engine

## 🎨 Design System

### Color Palette
- Primary Teal: `#008B8B`
- Secondary Teal: `#20B2AA`
- Light Accent: `#AFEEEE`
- Background: `#FAFEFE`

### UI Components
- **Button**: Primary, secondary, ghost variants
- **Card**: Consistent card design with headers
- **Badge**: Color-coded priority and tag indicators
- **Forms**: Consistent input styling

## 🚀 Deployment

### Backend Deployment
- Update CORS origins for production domain
- Set proper environment variables
- Use a production WSGI server like Gunicorn
- Consider using Docker for containerization

### Frontend Deployment
- Build the application: `npm run build`
- Deploy to Vercel, Netlify, or your preferred platform
- Update API endpoints to point to production backend

## 🤝 Contributing

1. Follow the cursor rules in `.cursorrules`
2. Always use virtual environments for Python development
3. Use TypeScript for all frontend code
4. Follow existing code structure and naming conventions
5. Test your changes before committing

## 🐛 Troubleshooting

### Backend Won't Start
1. Ensure .env has valid SUPABASE_URL, SUPABASE_TOKEN, AZURE_STORAGE_CONNECTION_STRING
2. Verify Supabase schema is applied
3. Check port 8001 is free

### Workflow Not Processing
1. Check /api/workflow/status
2. Ensure engine is running
3. Verify Supabase connection

### Import Errors
1. Make sure you're in the correct directory
2. Virtual environment is activated
3. All dependencies are installed
4. Use the `start_server.py` script which handles paths automatically

## 📄 License

[Add your license here]