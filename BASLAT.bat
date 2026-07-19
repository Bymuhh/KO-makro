@echo off
chcp 65001 >nul
title KO Makro
cd /d "%~dp0"

where python >nul 2>&1
if errorlevel 1 (
    echo Python bulunamadi. Once Python kurun veya PATH'e ekleyin.
    pause
    exit /b 1
)

python "ko_makro.py"
if errorlevel 1 (
    echo.
    echo HATA! Yukardaki mesaji kopyalayip ilet.
    pause
)
