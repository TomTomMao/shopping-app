@echo off
setlocal
cd /d "%~dp0"

if not exist "server\.env" (
  copy /Y "server\.env.example" "server\.env" >nul
  echo.
  echo [SceneForge] Created server\.env
  echo Fill in DEEPSEEK_API_KEY, QWEN_API_KEY and MESHY_API_KEY, then run run.bat again.
  start "" notepad "server\.env"
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo [SceneForge] Creating local Python environment...
  py -m venv .venv
  if errorlevel 1 (
    python -m venv .venv
  )
)

echo [SceneForge] Installing/updating dependencies...
".venv\Scripts\python.exe" -m pip install -q -r "server\requirements.txt"
if errorlevel 1 (
  echo [SceneForge] Dependency installation failed.
  pause
  exit /b 1
)

echo [SceneForge] Starting at http://127.0.0.1:8000
start "" powershell -NoProfile -WindowStyle Hidden -Command "Start-Sleep -Seconds 2; Start-Process 'http://127.0.0.1:8000'"
".venv\Scripts\python.exe" -m uvicorn server.app:app --host 127.0.0.1 --port 8000

endlocal
