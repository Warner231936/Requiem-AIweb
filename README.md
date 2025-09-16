# Requiem AI Web Portal

Requiem AI is a dark, mystical web portal that delivers an always-on conversational companion with transparent task progress tracking. The project ships with a FastAPI backend, a React + TailwindCSS frontend, a single shared configuration file, and Windows-friendly automation scripts.

## Table of Contents
- [Features](#features)
- [System Requirements](#system-requirements)
- [Configuration](#configuration)
- [Quick Start (Windows 10)](#quick-start-windows-10)
- [Manual Setup](#manual-setup)
  - [Backend](#backend)
  - [Frontend](#frontend)
- [Running the Portal](#running-the-portal)
- [Application Structure](#application-structure)
- [API Reference](#api-reference)
- [Progress Tracking Logic](#progress-tracking-logic)
- [Deployment Notes](#deployment-notes)
- [Troubleshooting](#troubleshooting)

## Features
- 🔐 **Secure authentication** with hashed passwords (bcrypt) and JWT access tokens.
- 🪄 **Immersive UI**: glowing "Requiem" branding, animated nebula background, neon accents, and responsive layout.
- 💬 **Real-time chat** with auto-scrolling dialogue bubbles and a mystical AI persona response generator.
- 📊 **Dynamic progress dashboard** that visualises task completion percentages with animated bars and overall completion.
- 🖼️ **Profile picture upload** during sign-up with media hosting by the backend.
- ⚙️ **Single source of configuration** (`config/settings.json`) covering app, security, database, frontend, and API options.
- 🪟 **Windows automation scripts** (`scripts/*.bat`) for installing and launching backend/frontend services.

## System Requirements
- Windows 10 (PowerShell or Command Prompt).
- Python 3.11+ and `pip` on PATH.
- Node.js 20+ and npm.
- Git for cloning.

Optional (production): a process manager such as NSSM or a Windows Service for FastAPI, and a reverse proxy (IIS/NGINX) for HTTPS.

## Configuration
All runtime settings live in **`config/settings.json`**. Key sections:

| Section | Purpose |
| --- | --- |
| `app` | FastAPI metadata and default host/port. |
| `security` | JWT secret, algorithm, and expiry minutes. **Change the secret key before going live.** |
| `database` | SQLAlchemy database URL (defaults to local SQLite). |
| `frontend` | UI strings and Tailwind animation timing. |
| `progress` | Seed tasks with initial completion percentages. |
| `chat` | Persona hint used by the responder. |
| `files` | Media directories for profile pictures. |
| `cors` | Allowed web origins. |
| `api` | Base URL used by the frontend dev server proxy. |

Edit this file to point to production resources (e.g., PostgreSQL URL, public hostnames). Restart the services after changes.

## Quick Start (Windows 10)
1. **Clone the repository**
   ```powershell
   git clone https://github.com/your-org/Requiem-AIweb.git
   cd Requiem-AIweb
   ```
2. **Install backend dependencies**
   ```powershell
   scripts\install_backend.bat
   ```
3. **Install frontend dependencies**
   ```powershell
   scripts\install_frontend.bat
   ```
4. **Launch everything** (opens two Command Prompt windows)
   ```powershell
   scripts\launch_portal.bat
   ```
5. Visit [http://localhost:5173](http://localhost:5173) to enter the Requiem portal.

## Manual Setup

### Backend
1. Create a virtual environment and install requirements:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate
   python -m pip install --upgrade pip
   pip install -r backend\requirements.txt
   ```
2. Run FastAPI with Uvicorn:
   ```powershell
   uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
   ```

### Frontend
1. Install dependencies:
   ```powershell
   cd frontend
   npm install
   ```
2. Start the Vite dev server:
   ```powershell
   npm run dev
   ```
   Vite proxies API requests to the FastAPI server using the shared config file.

## Running the Portal
- `scripts\launch_backend.bat` &mdash; start only the backend (`scripts\launch_backend.bat [host] [port]`).
- `scripts\launch_frontend.bat` &mdash; start only the frontend dev server.
- `scripts\launch_portal.bat` &mdash; start both in separate terminals.

To build the frontend for production:
```powershell
cd frontend
npm run build
```
Then copy `frontend\dist` to the server. The FastAPI app automatically serves the bundled assets when the directory exists.

## Application Structure
```
backend/
  auth.py           # Password hashing, JWT creation, dependency helpers
  config.py         # Loader for config/settings.json
  database.py       # SQLAlchemy engine and session factory
  main.py           # FastAPI app, CORS, startup hooks, static mounts
  models.py         # ORM models: User, Message, Task
  routers/
    auth.py         # Sign-up, login, profile
    chat.py         # Chat history + message posting
    progress.py     # Progress retrieval and updates
  schemas.py        # Pydantic request/response models
  services/
    responder.py    # Mystical AI response generator
config/
  settings.json     # Single source of truth for all settings
frontend/
  src/
    App.jsx         # Root UI with auth/chat/progress logic
    components/     # AuthPanel, ChatWindow, ProgressPanel
scripts/
  *.bat             # Windows installers and launchers
agents/
  NOTES.md          # Progress ledger for developers
media/profile_pics/ # Uploaded profile images
```

## API Reference
Base URL defaults to `http://localhost:8000`.

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/auth/signup` | Create a new account (multipart form with optional `profile_picture`). |
| `POST` | `/auth/login` | Obtain a JWT (`application/x-www-form-urlencoded`). |
| `GET` | `/auth/me` | Current user profile. Requires `Authorization: Bearer <token>`. |
| `GET` | `/chat/history?limit=100` | Fetch recent chat messages. |
| `POST` | `/chat/message` | Submit a user message and receive user/AI message pair. |
| `GET` | `/progress/` | Retrieve task list and overall progress. |
| `PUT` | `/progress/{task_id}` | Update a task (name/progress/description). |
| `POST` | `/progress/reset` | Reset tasks to the values in `settings.json`. |
| `GET` | `/health` | Simple health probe for monitoring. |

All authenticated routes expect a valid JWT from `/auth/login`.

## Progress Tracking Logic
- Tasks are seeded from `config/settings.json` on startup.
- Each time a chat message is posted, the earliest in-progress task advances by up to 7% (never exceeding 100%).
- Progress API responses include both per-task percentages and a computed overall completion value.
- The React dashboard refreshes progress automatically after every chat exchange.

## Deployment Notes
- Update `config/settings.json` with production hostnames, HTTPS origins, and a strong `jwt_secret_key`.
- Swap the `database.url` to PostgreSQL or MySQL for multi-user scale.
- Behind a domain such as `http://www.requiem-ai.online`, forward ports 80/443 to the Windows server. Configure reverse proxy/SSL separately (IIS URL Rewrite + Let’s Encrypt or an edge appliance).
- Consider running `uvicorn` behind a Windows service (NSSM or `sc create`) and serving the built frontend (`frontend/dist`) directly via FastAPI or a dedicated static host.
- Regularly back up the SQLite/PostgreSQL database file and uploaded `media/` directory.

## Troubleshooting
| Symptom | Resolution |
| --- | --- |
| `uvicorn` cannot start (module not found) | Activate the virtual environment or rerun `scripts\install_backend.bat`. |
| Login fails after signup | Ensure the password meets the 8-character minimum; check terminal logs for validation errors. |
| Frontend cannot reach backend | Confirm both services are running, check `config/settings.json` CORS origins, and verify firewall rules for ports 5173 and 8000. |
| Profile pictures not saving | Confirm the `media/profile_pics` directory is writable; Windows may require adjusted permissions. |
| Need to reset task data | Execute `POST /progress/reset` (Swagger UI available at `http://localhost:8000/docs`). |

Enter the portal and let Requiem guide your nocturnal builds.
