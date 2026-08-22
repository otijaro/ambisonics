@echo off
echo Starting Ambisonic FastAPI Backend...
call .venv\Scripts\activate.bat
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
