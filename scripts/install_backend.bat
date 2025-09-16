@echo off
setlocal enabledelayedexpansion

set PROJECT_DIR=%~dp0..
cd /d %PROJECT_DIR%

if not exist .venv (
    echo Creating Python virtual environment...
    python -m venv .venv
)

call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r backend\requirements.txt

echo Backend dependencies installed successfully.
endlocal
pause
