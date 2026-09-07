@echo off
setlocal EnableExtensions
pushd "%~dp0"

if exist ".venv\Scripts\python.exe" (
    set "PYTHON=.venv\Scripts\python.exe"
) else if exist ".venv\bin\python.exe" (
    set "PYTHON=.venv\bin\python.exe"
) else (
    where python >nul 2>nul
    if not errorlevel 1 (
        set "PYTHON=python"
    ) else (
        echo Python topilmadi. .venv ichidagi Python yoki global python ni o'rnatib chiqing.
        pause
        exit /b 1
    )
)

title Coverse server - port 8000

echo Coverse server ishga tushmoqda: http://localhost:8000
"%PYTHON%" restart_coverse.py
