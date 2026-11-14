#!/usr/bin/env bash
# ===================================================
#   Iniciando Ambisonic Backend (FastAPI / Uvicorn)
# ===================================================

if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
elif [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

if [ ! -f ".env" ]; then
    echo "[ADVERTENCIA] No se encontró el archivo .env."
    echo "Creando .env a partir de .env.example..."
    cp .env.example .env
fi

python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

