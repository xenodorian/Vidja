@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo Packaging Vidja_ComfyUI_Ready.zip ...
set "SRC=%~dp0ComfyUI_windows_portable"
if not exist "%SRC%" (
  echo Expected portable runtime folder not found: %SRC%
  echo Run Setup_Vidja_Windows.bat first.
  pause
  exit /b 1
)

set "ZIP=%~dp0Vidja_ComfyUI_Ready.zip"
if exist "%ZIP%" del /f /q "%ZIP%"

powershell -NoProfile -Command "Compress-Archive -Path '%SRC%\*' -DestinationPath '%ZIP%' -Force"
if errorlevel 1 (
  echo Packaging failed.
  pause
  exit /b 1
)

echo Created: %ZIP%
dir "%ZIP%"
pause
exit /b 0
