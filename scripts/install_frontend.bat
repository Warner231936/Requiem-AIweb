@echo off
setlocal

set PROJECT_DIR=%~dp0..
cd /d %PROJECT_DIR%\frontend

echo Installing frontend dependencies...
npm install

echo Frontend dependencies installed.
endlocal
pause
