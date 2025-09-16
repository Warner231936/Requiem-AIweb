@echo off
setlocal

set PROJECT_DIR=%~dp0..
cd /d %PROJECT_DIR%

if not exist .venv (
    echo Backend virtual environment missing. Run scripts\install_backend.bat first.
    pause
    exit /b 1
)

start "Requiem Backend" cmd /k "cd /d %PROJECT_DIR% && call .venv\Scripts\activate && uvicorn backend.main:app --host 0.0.0.0 --port 8000"
start "Requiem Frontend" cmd /k "cd /d %PROJECT_DIR%\frontend && npm run dev"

echo Launch commands issued. Two new windows should now be running the services.
endlocal
