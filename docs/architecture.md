# Architecture & System Design

## Overview
The Email Campaign Management System is built as a production-grade full-stack web application designed for high throughput, reliability, and security.

## System Topology

```
                  ┌───────────────────────────────┐
                  │         React (Vite)          │
                  │   Single Page App (Port 5173) │
                  └───────────────┬───────────────┘
                                  │ REST / JSON
                                  ▼
                  ┌───────────────────────────────┐
                  │        FastAPI Backend        │
                  │    JWT Auth & CORS (Port 8000)│
                  └───────┬───────────────┬───────┘
                          │               │
               SQLAlchemy │               │ Task Queue
                          ▼               ▼
                ┌──────────────────┐   ┌─────────────────┐
                │ PostgreSQL /     │   │      Redis      │
                │ SQLite Storage   │   │  Worker Queue   │
                └──────────────────┘   └────────┬────────┘
                                                │
                                                ▼
                                       ┌─────────────────┐
                                       │  Celery Worker  │
                                       │  (Email Engine) │
                                       └────────┬────────┘
                                                │
                                                ▼
                                           SMTP Server
```

## Key Layers
1. **Frontend**: Built with React 18, Vite, React Router, Tailwind CSS, Lucide icons, and Axios. Handles user interactions, template editing, CSV uploading, live campaign monitoring, and settings configuration.
2. **Backend API**: Developed with FastAPI & Pydantic v2. Provides REST endpoints for authentication, template management, CSV validation, campaign dispatch, settings, and health monitoring.
3. **Database**: Supports PostgreSQL (production) & SQLite (local development fallback). Managed via SQLAlchemy ORM & Alembic migrations.
4. **Worker Queue**: Uses Celery + Redis for asynchronous email dispatch. Prevents HTTP blocking during bulk emailing. Includes background thread fallback when Redis is absent.
5. **SMTP Engine**: Supports Gmail SMTP & standard TLS/SSL connections. Features automatic 3x retries with exponential backoff (2s, 4s, 8s).

