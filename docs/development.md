# Local Development Guide

## Prerequisites
- Python 3.10+
- Node.js 18+ and npm
- Git

## 1. Backend Setup
```bash
cd backend
python -m venv env
# On Windows:
.\env\Scripts\activate
# On Linux/macOS:
source env/bin/activate

pip install -r requirements.txt
```

Run FastAPI Backend server:
```bash
uvicorn app.main:app --reload --port 8000
```
Swagger UI will be available at `http://127.0.0.1:8000/docs`.

## 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open browser at `http://localhost:5173`.

## 3. Running Backend Tests
```bash
cd backend
pytest
```

