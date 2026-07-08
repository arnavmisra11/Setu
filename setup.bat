@echo off
cd /d "%~dp0"
echo Setting up Setu for the first time...
echo.

python -m venv venv
call venv\Scripts\activate

pip install -r requirements.txt

if not exist .env (
    copy .env.example .env
    echo.
    echo IMPORTANT: Open the .env file in Notepad and paste your Sarvam API key in it.
    echo Then double-click start.bat to launch Setu.
    notepad .env
) else (
    echo.
    echo Setup complete. Double-click start.bat to launch Setu.
)

pause
