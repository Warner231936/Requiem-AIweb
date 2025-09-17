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
- [Telemetry Agent](#telemetry-agent)
- [Operations Analytics & Monitoring](#operations-analytics--monitoring)
- [Security Utilities](#security-utilities)
- [Deployment Notes](#deployment-notes)
- [Troubleshooting](#troubleshooting)

## Features
- 🔐 **Secure authentication** with hashed passwords (bcrypt) and JWT access tokens.
- 🪄 **Immersive UI**: glowing "Requiem" branding, animated nebula background, neon accents, and responsive layout.
- 💬 **Real-time chat** with persona-driven responses and pluggable LLM providers (template, OpenAI, or local Ollama).
- 📊 **Dynamic progress dashboard** that visualises task completion percentages with animated bars and overall completion.
- 📡 **Live telemetry log** that records task events from chat annotations or API-driven job updates.
- 🤖 **Autonomous telemetry agent** that issues configurable background progress pulses for long-running tasks.
- 📈 **Operations analytics** endpoint, Prometheus metrics feed, and UI overlays for throughput insight.
- 🖼️ **Profile picture upload** during sign-up with media hosting by the backend.
- ⚙️ **Single source of configuration** (`config/settings.json`) covering app, security, database, frontend, and API options.
- 🧰 **Cross-platform automation scripts** (`scripts/*.bat` for Windows, `scripts/*.sh` for Linux) covering install and launch flows.

## System Requirements
- Windows 10 (PowerShell or Command Prompt) **or** Linux (tested on Ubuntu 22.04+/Debian-based with Bash 5+).
- Python 3.11+ and `pip` on PATH.
- Node.js 20+ and npm.
- Git for cloning.
- For Linux scripts: GNU `bash`, `coreutils`, and permission to execute shell scripts inside the repository.

Optional (production): a process manager such as NSSM or a Windows Service for FastAPI, and a reverse proxy (IIS/NGINX) for HTTPS.

## Configuration
All runtime settings live in **`config/settings.json`**. Key sections:

| Section | Purpose |
| --- | --- |
| `app` | FastAPI metadata and default host/port. |
| `security` | JWT secret, algorithm, and expiry minutes. **Change the secret key before going live.** |
| `database` | SQLAlchemy database URL (defaults to local SQLite). |
| `frontend` | UI strings and Tailwind animation timing. |
| `progress` | Seed tasks with initial completion percentages and optional descriptions. |
| `chat` | Persona hint and active provider (`template`, `openai`, or `ollama`). Replace `REPLACE_WITH_OPENAI_KEY` before enabling OpenAI. |
| `progress_settings` | Controls chat auto-increment, annotation source names, and telemetry history limits. |
| `telemetry_agent` | Enables/disables the background telemetry worker, intervals, and task overrides. |
| `files` | Media directories for profile pictures. |
| `cors` | Allowed web origins. |
| `api` | Base URL used by the frontend dev server proxy. |

Edit this file to point to production resources (e.g., PostgreSQL URL, public hostnames). Restart the services after changes.

### AI Provider Setup

The responder defaults to the internal **template** persona, so no external credentials are required. To switch providers:

1. **OpenAI API**
   - Set `"provider": "openai"` under the `chat` section.
   - Replace the placeholder `REPLACE_WITH_OPENAI_KEY` with a valid secret key.
   - Optionally adjust `model`, `temperature`, and `max_tokens`.
   - Restart the backend after editing the config.
2. **Local Ollama**
   - Install [Ollama](https://ollama.ai/) on Windows and pull a chat-capable model (e.g., `ollama pull llama3`).
   - Set `"provider": "ollama"` and update `base_url`/`model` if you run a custom instance.
   - Tune any generation parameters inside the `options` object.

The shared `request_timeout_seconds` value governs API calls for any remote provider.

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

## Quick Start (Linux)
1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/Requiem-AIweb.git
   cd Requiem-AIweb
   ```
2. **Install backend dependencies** (set `PYTHON_BIN` if your Python binary has a different name)
   ```bash
   ./scripts/install_backend.sh
   ```
3. **Install frontend dependencies**
   ```bash
   ./scripts/install_frontend.sh
   ```
4. **Launch everything** (press <kbd>Ctrl</kbd>+<kbd>C</kbd> to stop both services)
   ```bash
   ./scripts/launch_portal.sh
   ```
   The launcher reads default host/port values from `config/settings.json`. Override them via positional arguments:
   ```bash
   ./scripts/launch_portal.sh 0.0.0.0 8000 localhost 5173
   ```
5. Visit [http://localhost:5173](http://localhost:5173) to enter the Requiem portal.

## Manual Setup

### Backend
1. Create a virtual environment and install requirements:
   - **Windows (PowerShell)**
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\activate
     python -m pip install --upgrade pip
     pip install -r backend\requirements.txt
     ```
   - **Linux (Bash)**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     python -m pip install --upgrade pip
     pip install -r backend/requirements.txt
     ```
2. Run FastAPI with Uvicorn:
   - **Windows (PowerShell)**
     ```powershell
     uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
     ```
   - **Linux (Bash)**
     ```bash
     source .venv/bin/activate
     uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
     ```

### Frontend
1. Install dependencies:
   - **Windows (PowerShell)**
     ```powershell
     cd frontend
     npm install
     ```
   - **Linux (Bash)**
     ```bash
     cd frontend
     npm install
     ```
2. Start the Vite dev server (defaults read from `config/settings.json`):
   - **Windows (PowerShell)**
     ```powershell
     npm run dev
     ```
   - **Linux (Bash)**
     ```bash
     npm run dev -- --host localhost --port 5173
     ```
   Vite proxies API requests to the FastAPI server using the shared config file.

## Running the Portal
- **Windows automation**
  - `scripts\launch_backend.bat` &mdash; start only the backend (`scripts\launch_backend.bat [host] [port]`).
  - `scripts\launch_frontend.bat` &mdash; start only the frontend dev server.
  - `scripts\launch_portal.bat` &mdash; start both in separate terminals.
- **Linux automation**
  - `scripts/launch_backend.sh` &mdash; start only the backend (`./scripts/launch_backend.sh [host] [port]`, defaults from `config/settings.json`).
  - `scripts/launch_frontend.sh` &mdash; start only the frontend dev server (`./scripts/launch_frontend.sh [host] [port]`).
  - `scripts/launch_portal.sh` &mdash; start both in the current terminal (`./scripts/launch_portal.sh [backend_host] [backend_port] [frontend_host] [frontend_port]`).

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
  *.sh              # Linux installers and launchers
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
| `GET` | `/progress/` | Retrieve task list, telemetry events, and overall progress. |
| `PUT` | `/progress/{task_id}` | Update a task (name/progress/description). |
| `POST` | `/progress/reset` | Reset tasks to the values in `settings.json`. |
| `POST` | `/progress/events` | Record a progress event for a task (creates it if missing). |
| `GET` | `/progress/events` | Fetch the most recent task events (respecting the configured history limit). |
| `GET` | `/health` | Simple health probe for monitoring. |

All authenticated routes expect a valid JWT from `/auth/login`.

## Progress Tracking Logic
- Tasks are seeded from `config/settings.json` on startup and may include descriptions for the dashboard.
- Embed `[progress|Task Name|90|optional note]` inside any chat message to log a telemetry event and update that task to 90%.
- The `/progress/events` endpoint (and dashboard log) show the most recent events up to the configured history limit.
- When no annotations are detected, the backend optionally auto-advances the oldest incomplete task by the configured step.
- The React dashboard refreshes both tasks and event telemetry after every chat exchange.

### Reporting Progress via API

External workers can record the same telemetry without going through chat:

```powershell
curl -X POST http://localhost:8000/progress/events ^
  -H "Authorization: Bearer <TOKEN>" ^
  -H "Content-Type: application/json" ^
  -d "{\"task_name\":\"Training Model\",\"progress\":75,\"note\":\"Epoch 12 complete\"}"
```

The event source defaults to `api`, but you can override it per request. History depth, chat annotation source, and auto-increment behaviour all live under `progress_settings` in `config/settings.json`.

## Telemetry Agent

Requiem now ships with an autonomous telemetry worker that keeps task updates flowing even when no chat annotations arrive. Configure it via the `telemetry_agent` block inside `config/settings.json`:

```json
"telemetry_agent": {
  "enabled": true,
  "interval_seconds": 60,
  "max_tasks_per_cycle": 2,
  "source": "automation-pipeline",
  "default_step": 6,
  "note_template": "Automated pipeline advanced {task} to {progress}%.",
  "task_overrides": {
    "Training Model": { "step": 4, "note": "Training cluster reported a fresh epoch." }
  }
}
```

- **enabled** — turns the worker on or off.
- **interval_seconds** — cadence (in seconds) between telemetry pulses.
- **max_tasks_per_cycle** — limits how many tasks receive an update per tick.
- **default_step** — increment applied to tasks without overrides.
- **note_template** — format string supporting `{task}`, `{progress}`, and `{timestamp}`.
- **task_overrides** — per-task step sizes and custom notes.

The agent starts automatically with the FastAPI application and shuts down cleanly when the server stops.

## Operations Analytics & Monitoring

- **`GET /progress/analytics`** (JWT protected) returns aggregated task statistics such as completion counts, source breakdowns, per-task event history, and estimated completion times.
- The frontend dashboard renders these metrics in the *Operations Analytics* panel for at-a-glance insight into throughput and recent telemetry.
- **`GET /monitoring/metrics`** emits Prometheus-compatible gauges and counters so that Prometheus, Datadog, or other monitoring suites can scrape live task health.

## Security Utilities

Rotate authentication secrets without manual edits:

```powershell
scripts\rotate_jwt_secret.bat --length 80
```

The helper generates a fresh random key and rewrites `config/settings.json`, leaving a short preview of the previous secret in the console for audit logs.

## Deployment Notes
- Update `config/settings.json` with production hostnames, HTTPS origins, and a strong `jwt_secret_key`.
- Swap the `database.url` to PostgreSQL or MySQL for multi-user scale.
- Behind a domain such as `http://www.requiem-ai.online`, forward ports 80/443 to the Windows server. Configure reverse proxy/SSL separately (IIS URL Rewrite + Let’s Encrypt or an edge appliance).
- Consider running `uvicorn` behind a Windows service (NSSM or `sc create`) and serving the built frontend (`frontend/dist`) directly via FastAPI or a dedicated static host.
- Expose `/monitoring/metrics` to your observability stack for real-time task visibility.
- Tune or disable the telemetry agent when external systems provide authoritative progress updates.
- Regularly back up the SQLite/PostgreSQL database file and uploaded `media/` directory.

## Troubleshooting
| Symptom | Resolution |
| --- | --- |
| `uvicorn` cannot start (module not found) | Activate the virtual environment or rerun `scripts\install_backend.bat`. |
| Login fails after signup | Ensure the password meets the 8-character minimum; check terminal logs for validation errors. |
| Frontend cannot reach backend | Confirm both services are running, check `config/settings.json` CORS origins, and verify firewall rules for ports 5173 and 8000. |
| Profile pictures not saving | Confirm the `media/profile_pics` directory is writable; Windows may require adjusted permissions. |
| Need to reset task data | Execute `POST /progress/reset` (Swagger UI available at `http://localhost:8000/docs`). |
| OpenAI provider fails with 401/429 | Double-check the API key in `config/settings.json`, ensure billing is active, and confirm outbound internet access. |

Enter the portal and let Requiem guide your nocturnal builds.
