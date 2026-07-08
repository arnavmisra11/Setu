@echo off
cd /d "%~dp0"

if not exist venv (
    echo Setu hasn't been set up yet. Double-click setup.bat first.
    pause
    exit /b
)

call venv\Scripts\activate

echo Starting Setu...
start "" http://localhost:3000
python app.py

pause
