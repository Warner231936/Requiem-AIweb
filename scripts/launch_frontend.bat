@echo off
setlocal

set PROJECT_DIR=%~dp0..
cd /d %PROJECT_DIR%\frontend

echo Starting Requiem frontend on the configured dev server port...
npm run dev

endlocal
