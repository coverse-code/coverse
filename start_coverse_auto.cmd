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

cls
echo Coverse server ishga tushmoqda: http://127.0.0.1:8000/app
"%PYTHON%" restart_coverse.py
