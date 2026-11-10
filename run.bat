@echo off
setlocal
cd /d "%~dp0"

if exist ".venv\Scripts\pythonw.exe" (
    start "" ".venv\Scripts\pythonw.exe" -m english_exercise
    exit /b 0
)

where uv >nul 2>nul
if %errorlevel%==0 (
    uv run english-exercise-gui
    exit /b 0
)

echo 未找到 .venv 或 uv，请先运行：uv sync
pause
