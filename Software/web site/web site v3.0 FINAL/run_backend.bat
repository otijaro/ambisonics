@echo off
chcp 65001 > nul
echo ===================================================
echo   Iniciando Ambisonic Backend (FastAPI / Uvicorn)
echo ===================================================

if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
) else if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

if not exist ".env" (
    echo [ADVERTENCIA] No se encontro el archivo .env.
    echo Creando .env a partir de .env.example...
    copy .env.example .env
    echo Por favor edita .env con tus credenciales de PostgreSQL si deseas usar cuentas.
)

python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
pause

