# nxtLvl - Next.js + FastAPI Full Stack Application

A modern full-stack web application built with Next.js (TypeScript + Tailwind CSS) frontend and FastAPI (Python) backend.

## 🏗️ Project Structure

```
nxtLvl/
├── frontend/                 # Next.js frontend
│   ├── src/
│   │   ├── app/             # App Router pages
│   │   ├── components/      # Reusable components
│   │   └── lib/            # Utility functions
│   ├── public/             # Static assets
│   ├── package.json        # Node.js dependencies
│   └── tailwind.config.js  # Tailwind configuration
├── backend/                 # FastAPI backend
│   ├── venv/               # Python virtual environment (not in git)
│   ├── app/
│   │   ├── main.py         # FastAPI app entry point
│   │   ├── models/         # Pydantic models
│   │   ├── routes/         # API routes
│   │   └── utils/          # Utility functions
│   ├── requirements.txt    # Python dependencies
│   ├── start_server.py     # Easy server startup script
│   ├── run.bat            # Windows batch file to start server
│   └── env.example         # Environment variables template
└── README.md              # This file
```

## 🚀 Quick Start

### Prerequisites

- **Node.js** (v18+)
- **Python** (v3.11+)
- **npm** or **yarn**

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd nxtLvl
```

### 2. Backend Setup (FastAPI)

#### Option A: Using the startup script (Recommended)
```bash
# Navigate to backend
cd backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run the server (handles all imports automatically)
python start_server.py
```

#### Option B: Using the batch file (Windows only)
```bash
cd backend
.\run.bat
```

#### Option C: Manual uvicorn
```bash
cd backend
venv\Scripts\activate
$env:PYTHONPATH="."  # Windows PowerShell
uvicorn app.main:app --reload --port 8003
```

The API will be available at: `http://localhost:8003`
- API docs: `http://localhost:8003/docs`
- Health check: `http://localhost:8003/api/health`
- Automations: `http://localhost:8003/api/automations/`

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

The backend uses port 8003 to avoid Windows permission issues with port 8000.

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
uvicorn app.main:app --reload --port 8003
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

- Backend: `http://localhost:8003` (changed from 8000 to avoid Windows permission issues)
- Frontend: `http://localhost:3000`
- API proxy: Frontend proxies `/api/*` to backend automatically

## 📦 Tech Stack

### Frontend
- **Framework**: Next.js 15.4+
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Components**: Custom UI library with teal theme
- **Architecture**: App Router with route groups

### Backend
- **Framework**: FastAPI 0.115+
- **Language**: Python 3.11+
- **Server**: Uvicorn
- **Validation**: Pydantic
- **Environment**: python-dotenv
- **Storage**: In-memory (MVP, replace with DB later)

## 🏢 Application Features

### Current MVP Features
- **Dashboard**: Overview of all modules
- **Automation Pipeline**: Kanban-style workflow with 5 stages:
  - New
  - Classification
  - Data Extraction
  - Processing
  - Done
- **CRUD Operations**: Create, read, update, delete automation items
- **Real-time Updates**: Changes reflect immediately
- **Responsive Design**: Works on desktop and mobile
- **Loading States**: Skeleton screens for better UX

### Placeholder Pages (Ready for Implementation)
- **Pipeline Config**: Configure stages and rules
- **Agentic Rules**: Define automation rules
- **Integration**: Connect external systems
- **Settings**: Application preferences

### Backend API
- **GET /api/automations/**: List all automations
- **POST /api/automations/**: Create new automation
- **GET /api/automations/{id}**: Get specific automation
- **PATCH /api/automations/{id}**: Update automation
- **DELETE /api/automations/{id}**: Delete automation
- **GET /api/health**: Health check

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
1. Make sure you're in the `backend` directory
2. Activate the virtual environment: `venv\Scripts\activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Use the startup script: `python start_server.py`
5. If port 8000 is blocked, the app uses port 8003

### Frontend API Calls Fail
1. Make sure backend is running on port 8003
2. Check `frontend/next.config.ts` has correct destination port
3. Restart frontend dev server after changing config

### Import Errors
1. Make sure you're in the correct directory
2. Virtual environment is activated
3. All dependencies are installed
4. Use the `start_server.py` script which handles paths automatically

## 📄 License

[Add your license here]