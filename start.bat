@echo off
echo ==========================================================
echo  STARTING AI ROBOTICS DESIGN STUDIO (SW 2024 + 2026)
echo ==========================================================
echo.
echo [1/2] Launching Backend on http://localhost:8000 ...
start "Studio Backend" python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

echo [2/2] Launching Frontend on http://localhost:5173 ...
cd frontend
if not exist node_modules (
    echo [INFO] Installing frontend dependencies (one-time setup)...
    call npm install
)
start "Studio Frontend" cmd /k "npm run dev"
cd ..

echo.
echo ==========================================================
echo  Studio is running! Open your browser: http://localhost:5173
echo ==========================================================
