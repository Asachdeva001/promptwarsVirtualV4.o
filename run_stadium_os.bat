@echo off
title StadiumOS Launcher - FIFA World Cup 2026
echo ========================================================
echo               STADIUMOS PLATFORM LAUNCHER
echo ========================================================
echo.

:: Check for backend virtual environment setup
if not exist "backend\venv" (
    echo [System] Creating Python virtual environment in backend\venv...
    python -m venv backend\venv
    if errorlevel 1 (
        echo [Error] Failed to create virtual environment. Ensure Python is in your PATH.
        pause
        exit /b 1
    )
    echo [System] Installing backend dependencies...
    call backend\venv\Scripts\activate
    pip install -r backend\requirements.txt
) else (
    echo [System] Found existing Python virtual environment.
    echo [System] Ensuring backend dependencies are up to date...
    call backend\venv\Scripts\activate
    pip install -r backend\requirements.txt
)
:: Start FastAPI Backend
echo [System] Launching FastAPI Backend on port 8000...
start "StadiumOS Backend (Port 8000)" cmd /k "call backend\venv\Scripts\activate && cd backend && python run_backend.py"

:: Start Vite React Frontend
echo [System] Launching Vite React Frontend on port 3000...
start "StadiumOS Frontend (Port 3000)" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================================
echo SUCCESS: StadiumOS Services have been launched in separate terminals!
echo - Frontend Interface: http://localhost:3000
echo - Backend API Docs:  http://localhost:8000/docs
echo ========================================================
echo.
pause
