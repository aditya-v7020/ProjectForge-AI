@echo off
echo ===================================================
echo ProjectForge AI — Local Development Setup
echo ===================================================

echo Creating virtual environment...
python -m venv venv
call venv\Scripts\activate

echo Installing backend dependencies...
pip install -r backend\requirements.txt

echo Installing frontend dependencies...
pip install -r frontend\requirements.txt

if not exist .env (
    echo Creating .env file from .env.example...
    copy .env.example .env
    echo Please edit .env and enter your API keys.
)

echo Setup completed successfully!
echo To run backend: uvicorn backend.app.main:app --reload --port 8000
echo To run frontend: python frontend\manage.py runserver 8001
