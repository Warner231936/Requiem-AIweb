@echo off
setlocal
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%.."
if not exist config\settings.json (
  echo Configuration file not found in %CD%\config\settings.json
  exit /b 1
)
python "%SCRIPT_DIR%rotate_jwt_secret.py" %*
endlocal
