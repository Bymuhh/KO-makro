@echo off
chcp 65001 >nul
title Auto Key - EXE Derleme
cd /d "%~dp0"

set PY=C:\Users\Bymuhh\AppData\Local\Python\pythoncore-3.14-64\python.exe
if not exist "%PY%" set PY=python

echo PyInstaller kontrol ediliyor...
"%PY%" -m pip install pyinstaller --quiet
if errorlevel 1 (
    echo pip / PyInstaller kurulumu basarisiz.
    pause
    exit /b 1
)

echo.
echo Auto Key.exe derleniyor (birkaç dakika surebilir)...
"%PY%" -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --onefile ^
  --windowed ^
  --uac-admin ^
  --name "Auto Key" ^
  --distpath "%~dp0" ^
  --workpath "%~dp0build" ^
  --specpath "%~dp0" ^
  --hidden-import floody ^
  --add-data "%~dp0Icon;Icon" ^
  "%~dp0Auto Key.py"

if errorlevel 1 (
    echo.
    echo Derleme basarisiz.
    pause
    exit /b 1
)

echo.
echo Tamam: %~dp0Auto Key.exe
echo Icon klasoru ve floody.py exe ile ayni dizinde kalsin.
pause
