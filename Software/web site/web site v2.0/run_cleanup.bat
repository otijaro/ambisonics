@echo off
set "PROJECT_DIR=%~dp0"
set "PYTHON_EXE=%PROJECT_DIR%.venv\Scripts\python.exe"
set "CLEANUP_SCRIPT=%PROJECT_DIR%backend\services\cleanup.py"

set "PYTHONPATH=%PROJECT_DIR%"
echo Ejecutando limpieza de archivos temporales...
"%PYTHON_EXE%" "%CLEANUP_SCRIPT%"
exit /b %ERRORLEVEL%
