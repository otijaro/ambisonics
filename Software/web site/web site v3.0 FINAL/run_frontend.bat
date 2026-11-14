@echo off
chcp 65001 > nul
echo ===================================================
echo   Iniciando Ambisonic Frontend (Next.js)
echo ===================================================

where pnpm >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    pnpm dev
) else (
    npm run dev
)
pause

