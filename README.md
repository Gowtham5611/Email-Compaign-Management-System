# 📧 Email Campaign Management System (GUI-Based)
# 📧 Email Campaign Management System (Enterprise Web Edition v2.0)

An **industry-grade, GUI-based Email Campaign Management System** built using **Python and Tkinter**.  
This application allows users to upload a CSV file containing recipient details and send personalized emails in bulk using SMTP (Gmail supported), with progress tracking, logging, and preview functionality.
A production-ready, full-stack **Email Campaign Management Platform** built with **React, Vite, FastAPI, PostgreSQL, Redis, Celery, and Docker**.

This system upgrades the legacy Tkinter desktop application into a cloud-native web platform while preserving all existing email, CSV validation, dynamic template interpolation, SMTP configuration, file attachment, backoff retries, campaign cancellation, and activity logging features.

---

## 🚀 Features
## 🚀 Key Features Preserved & Upgraded

- 📄 **CSV Upload & Validation**
  - Upload recipient data using a CSV file
  - Validates email format automatically
  - Displays valid rows count before sending
- 📄 **CSV Upload & Intelligent Validation**
  - Instant CSV header & email syntax parsing (`[^@]+@[^@]+\.[^@]+`)
  - Detailed validation summary: Total rows, Valid count, Invalid count, Duplicate emails count
  - Row-by-row error inspection logging (missing fields, invalid email, duplicates)
  - Bulk import of valid recipients into PostgreSQL

- ✉️ **Personalized Email Sending**
  - Uses dynamic placeholders (`{name}`, `{subject}`)
  - Supports plain text email templates
  - Optional file attachment support
- ✉️ **Dynamic Template Management & Placeholders**
  - Database-backed templates with CRUD, duplication, and live rendering preview
  - Support for standard placeholders (`{name}`, `{subject}`, `{email}`) and **dynamic custom CSV attributes** (e.g. `{position}`, `{company}`)
  - Safe placeholder rendering (prevents application crashes when tags are missing)

- 🖥️ **Graphical User Interface (GUI)**
  - Built using Tkinter
  - User-friendly and non-technical friendly
  - Supports minimize, maximize, and fullscreen
- 📡 **SMTP Configuration & Security**
  - Per-user or global SMTP server, port, TLS/SSL toggle, and sender display name
  - Live "Test Connection" tool
  - Encrypted server-side password storage (never exposed in plain text)

- 📊 **Progress Tracking**
  - Real-time progress bar
  - Live status updates during sending
- 📎 **File Attachments & Security**
  - Attach files to campaigns with size limit checks & filename sanitization (protects against path traversal)

- 📝 **Live Logs Panel**
  - Displays real-time email activity
  - Scrollable, high-contrast, readable logs
  - Persistent log file stored locally
- 🔄 **Asynchronous Background Worker & Retries**
  - Non-blocking execution via **Celery + Redis** (with automatic threaded worker fallback)
  - 3x retries with exponential backoff (2s, 4s, 8s...)
  - Live campaign progress monitoring (percentage, sent, failed, cancelled, pending counts)
  - Safe **Campaign Cancellation** (halts pending dispatches without interrupting active transmissions)

- 🔍 **Email Preview**
  - Preview the first email before sending
  - Helps avoid mistakes in templates
- 📊 **Enterprise Dashboard & History**
  - Summary metrics, success rate charts, recent campaign activity
  - Historical campaign log with recipient-level delivery results & failure tracebacks

- ⚙️ **SMTP Configuration Panel**
  - Configure SMTP server and port
  - Configuration saved using `config.json`

- 🎨 **Professional UI**
  - Color-coded action buttons:
    - 🟢 Start (Send)
    - 🔵 Preview
    - 🔴 Stop
    - ⚫ Open Logs

- 📦 **Executable Support**
  - Can be converted into a standalone `.exe` using PyInstaller

---

## 🛠️ Tech Stack
## 🛠️ Technology Stack

- **Language:** Python 3.x  
- **GUI:** Tkinter  
- **Email:** `smtplib`, `email.mime`  
- **File Handling:** CSV, JSON  
- **Threading:** Background email sending  
- **Packaging:** PyInstaller  
| Layer | Technology |
|---|---|
| **Frontend** | React 18, Vite, Tailwind CSS, Lucide React, Recharts, Axios, React Router v6 |
| **Backend API** | Python 3.11+, FastAPI, Pydantic v2, Passlib (bcrypt), PyJWT |
| **Database & ORM** | PostgreSQL / SQLite fallback, SQLAlchemy 2.0, Alembic Migrations |
| **Queue & Worker** | Redis 7, Celery 5.3 |
| **Containerization** | Docker, Docker Compose, Nginx |

---

## 📂 Project Structure

```
Email_Campaign_Management_System/
│
├── gui_email_sender.py # Main GUI application
├── email_utils.py # Email sending and logging utilities
├── config.py # Email credentials (App Password)
├── config.json # Saved SMTP configuration
├── email_template.txt # Email body template
├── recipients.csv # Sample CSV file
├── logs/
│ └── activity_log.txt # Email activity logs
├── app_icon.ico # Application icon
├── README.md # Project documentation
├── frontend/                  # React Single Page App
│   ├── src/
│   │   ├── components/        # UI components
│   │   ├── context/           # JWT Auth context
│   │   ├── layouts/           # Sidebar & top navigation layout
│   │   ├── pages/             # Login, Dashboard, Templates, Recipients, Campaigns, History, Settings
│   │   ├── services/          # Axios API client
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   ├── Dockerfile
│   └── nginx.conf
│
├── backend/                   # FastAPI Backend
│   ├── app/
│   │   ├── api/               # Auth, Templates, Recipients, Campaigns, Settings, Dashboard routes
│   │   ├── core/              # Config, Security (JWT/bcrypt), Logging
│   │   ├── database/          # SQLAlchemy Database & Models
│   │   ├── schemas/           # Pydantic Schemas
│   │   ├── services/          # Email service (SMTP + backoff retries), CSV service, Template engine
│   │   ├── workers/           # Celery background email worker
│   │   └── main.py            # FastAPI Application entrypoint
│   ├── tests/                 # Pytest suite
│   ├── requirements.txt
│   ├── Dockerfile
│   └── alembic.ini
│
├── database/                  # Migrations
│   └── migrations/
│
├── uploads/                   # Secure Attachment Storage
├── logs/                      # Activity Log Storage
├── legacy/                    # Archived original Tkinter desktop codebase
├── docs/                      # Technical Documentation (architecture, API, deployment, development)
├── .env.example               # Environment Variables Template
├── docker-compose.yml         # Container Orchestration Manifest
├── README.md
└── LICENSE
```

---

📝 Email Template Format
Hello {name},
## ⚡ How to Run Locally

This is a reminder regarding: {subject}.
### Option A: Using Docker Compose (Recommended)

Regards,
Automation Team
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

Use Cases
2. Launch all services:
   ```bash
   docker-compose up --build
   ```

Internship / Academic projects
Internal company notifications
HR bulk communication
Event reminders
Marketing & outreach automation (small scale)
3. Open your browser:
   - **Frontend App**: `http://localhost` (Port 80) or `http://localhost:5173`
   - **FastAPI OpenAPI Swagger Docs**: `http://localhost:8000/docs`
   - **Health Endpoint**: `http://localhost:8000/health`

📈 Industry Evaluation
---

✔ Clean architecture
✔ GUI-based automation
✔ Safe credential handling
✔ Threaded execution
✔ Logging & validation
✔ Production-ready design
### Option B: Local Manual Execution (Without Docker)

#### 1. Backend:
```bash
cd backend
python -m venv env
# Activate venv:
# Windows: .\env\Scripts\activate | macOS/Linux: source env/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

👨‍💻 Author
#### 2. Frontend:
```bash
cd frontend
npm install
npm run dev
```

Gowtham R
Front-End & Python Developer
Email Campaign Management Systems | GUI Applications
---

## 🔒 Security Requirements & Recommendations

> [!IMPORTANT]
> **Revoke Hardcoded Legacy Credentials:**
> The legacy repository contained hardcoded credentials in `legacy/config.py`. These credentials have **not** been imported into the new codebase. Please revoke/rotate your Gmail App Password in your Google Account Security Settings immediately.

---

## 🧪 Running Automated Tests

Run backend tests using `pytest`:
```bash
cd backend
pytest
```

---

## 👨‍💻 Author & Maintainer

Gowtham R  
Full-Stack & Python Developer  
*Email Campaign Management Systems*