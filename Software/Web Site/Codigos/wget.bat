@echo off
if "%~1"=="-O" (
    if exist "%~2" (
        echo %~2 already exists, skipping download.
        exit /b 0
    )
    curl -L -o "%~2" "%~3"
) else (
    curl -L %*
)
