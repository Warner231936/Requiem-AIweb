@echo off
setlocal

set PROJECT_DIR=%~dp0..
cd /d %PROJECT_DIR%

if not exist .venv (
    echo Virtual environment missing. Run scripts\install_backend.bat first.
    pause
    exit /b 1
)

call .venv\Scripts\activate

set HOST=%1
if "%HOST%"=="" set HOST=0.0.0.0

set PORT=%2
if "%PORT%"=="" set PORT=8000

uvicorn backend.main:app --host %HOST% --port %PORT% --reload

endlocal
