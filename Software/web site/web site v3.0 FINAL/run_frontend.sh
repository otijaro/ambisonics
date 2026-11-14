#!/usr/bin/env bash
# ===================================================
#   Iniciando Ambisonic Frontend (Next.js)
# ===================================================

if command -v pnpm &> /dev/null; then
    pnpm dev
else
    npm run dev
fi

