@echo off
echo Starting Ambisonic FastAPI Backend...
call .venv\Scripts\activate.bat
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
