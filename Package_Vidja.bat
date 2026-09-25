@echo off
setlocal
set "ROOT=%~dp0"
set "SOURCE=%ROOT%Vidja_Portable"
set "OUTPUT=%ROOT%Vidja_ComfyUI_Ready.zip"

if not exist "%SOURCE%\ComfyUI\main.py" (
    echo ERROR: Run Setup_Vidja_Windows.bat first.
    exit /b 1
)

if exist "%OUTPUT%" del /f /q "%OUTPUT%"

echo Creating the single distributable ZIP.
tar -caf "%OUTPUT%" -C "%ROOT%" Vidja_Portable
if errorlevel 1 (
    echo ERROR: ZIP creation failed.
    exit /b 1
)

echo.
echo Created:
echo %OUTPUT%
echo.
