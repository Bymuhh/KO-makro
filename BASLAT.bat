@echo off
chcp 65001 >nul
title Auto Key
"C:\Users\Bymuhh\AppData\Local\Python\pythoncore-3.14-64\python.exe" "C:\Users\Bymuhh\Desktop\Auto Key\Auto Key.py"
if errorlevel 1 (
    echo.
    echo HATA! Yukardaki mesaji kopyalayip ilet.
    pause
)
