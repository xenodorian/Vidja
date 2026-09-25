@echo off
setlocal
cd /d "%~dp0"
echo.
echo ============================================================
echo VIDJA AUTOMATIC SETUP
echo ============================================================
echo This is the only setup step. It downloads, installs,
echo configures, tests, and launches the Vidja ComfyUI runtime.
echo.
where curl.exe >nul 2>&1 || (
  echo ERROR: Windows curl.exe is required.
  pause
  exit /b 1
)
where powershell.exe >nul 2>&1 || (
  echo ERROR: Windows PowerShell is required.
  pause
  exit /b 1
)
if not exist "%~dp0vidja_setup.py" (
  echo ERROR: vidja_setup.py is missing.
  pause
  exit /b 1
)
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "$p=Get-Command python.exe -ErrorAction SilentlyContinue; if($p){& $p.Source '%~dp0vidja_setup.py'; exit $LASTEXITCODE}else{exit 9009}"
if %ERRORLEVEL% EQU 9009 (
  echo No system Python was found. Downloading the official Python launcher is unnecessary:
  echo Vidja will use the embedded Python supplied by ComfyUI after extraction.
  echo.
  echo ERROR: The bootstrap helper requires a system Python 3.10+.
  echo Install Python from python.org with the launcher enabled, then rerun this file.
  pause
  exit /b 1
)
if not %ERRORLEVEL% EQU 0 (
  echo.
  echo VIDJA SETUP FAILED. See Vidja_Setup.log for the exact failure.
  pause
  exit /b 1
)
echo.
echo VIDJA SETUP COMPLETED.
echo ComfyUI should now be running and the browser should be open.
pause
