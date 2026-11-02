@echo off
title Geosense AI Platform Launcher
echo ===================================================
echo Starting Geosense Backend & Frontend Servers...
echo ===================================================

start "Geosense Backend (Port 8001)" cmd /k "cd /d %~dp0 && backend\venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8001 --reload"

start "Geosense Frontend (Port 8080)" cmd /k "cd /d %~dp0 && powershell -ExecutionPolicy Bypass -File .\server.ps1"

echo.
echo Both servers have been launched!
echo Public Landing Page: http://localhost:8080/
echo Private Dashboard:   http://localhost:8080/dashboard
echo API Documentation:   http://127.0.0.1:8001/docs
echo ===================================================
pause

