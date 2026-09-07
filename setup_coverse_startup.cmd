@echo off
setlocal EnableExtensions
pushd "%~dp0"

set "VBS=%~dp0keep_coverse_running.vbs"

for %%I in ("%VBS%") do reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "Coverse Local Server" /t REG_SZ /d "wscript.exe %%~sI" /f >nul
if errorlevel 1 (
    echo Avto-ishga tushirishni sozlab bo'lmadi.
    pause
    exit /b 1
)

echo Coverse Windows tizimiga kirilganda avtomatik ishga tushadi.
echo Manzil: http://127.0.0.1:8000/app
echo Hozir serverni ishga tushirish uchun start_coverse_auto.cmd faylini oching.
pause