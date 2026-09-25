@echo off
setlocal
cd /d "%~dp0"
set "BOOT=%~dp0_bootstrap_python"
set "PYZIP=%~dp0_downloads\python-3.13.15-embed-amd64.zip"

echo.
echo ============================================================
echo VIDJA AUTOMATIC SETUP
echo ============================================================
echo One-click mode: downloading, installing, verifying,
echo GPU-testing, and launching Vidja automatically.
echo.

if not exist "%~dp0vidja_setup.py" (
  echo ERROR: vidja_setup.py is missing.
  pause
  exit /b 1
)

where curl.exe >nul 2>&1 || (
  echo ERROR: Windows curl.exe is required.
  pause
  exit /b 1
)

if not exist "%BOOT%\python.exe" (
  echo Downloading isolated Python bootstrap...
  if not exist "%~dp0_downloads" mkdir "%~dp0_downloads"
  curl.exe -L --fail --retry 8 --retry-delay 3 "https://www.python.org/ftp/python/3.13.15/python-3.13.15-embed-amd64.zip" -o "%PYZIP%"
  if errorlevel 1 (
    echo ERROR: Could not download Python.
    pause
    exit /b 1
  )
  if exist "%BOOT%" rmdir /s /q "%BOOT%"
  mkdir "%BOOT%"
  powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "Expand-Archive -LiteralPath '%PYZIP%' -DestinationPath '%BOOT%' -Force"
  if errorlevel 1 (
    echo ERROR: Could not extract Python.
    pause
    exit /b 1
  )
)

"%BOOT%\python.exe" "%~dp0vidja_setup.py"
if errorlevel 1 (
  echo.
  echo VIDJA SETUP FAILED.
  echo See Vidja_Setup.log and Vidja_ComfyUI.log for exact diagnostics.
  pause
  exit /b 1
)

echo.
echo ============================================================
echo VIDJA SETUP COMPLETE
echo ============================================================
echo A real Wan GPU smoke test has completed successfully.
echo ComfyUI is running at http://127.0.0.1:8188
echo.
pause
