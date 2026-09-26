@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

echo ========================================
echo   Vidja autonomous Windows setup
echo   Target: NVIDIA RTX 3060 12GB
echo ========================================
echo.

set "LOG=%~dp0Vidja_Setup.log"
echo [%DATE% %TIME%] Starting Setup_Vidja_Windows.bat > "%LOG%"

REM Prefer an already-available python, otherwise bootstrap a local one.
set "PY="
where python >nul 2>&1 && set "PY=python"
if not defined PY where py >nul 2>&1 && set "PY=py -3"
if not defined PY (
  echo No system Python found. Bootstrapping a local Python 3.13...
  echo [%DATE% %TIME%] Bootstrapping local Python >> "%LOG%"
  call :bootstrap_python
  if errorlevel 1 (
    echo Failed to bootstrap Python. See Vidja_Setup.log
    pause
    exit /b 1
  )
  set "PY=%~dp0python_bootstrap\python.exe"
)

echo Using: %PY%
echo [%DATE% %TIME%] Using Python: %PY% >> "%LOG%"

"%PY%" -u "%~dp0vidja_setup.py" %*
set "RC=%ERRORLEVEL%"
echo [%DATE% %TIME%] vidja_setup.py exited with %RC% >> "%LOG%"
if not "%RC%"=="0" (
  echo.
  echo Setup failed. Keep Vidja_Setup.log and Vidja_ComfyUI.log
  echo Record the failure in Current_Work.md
  pause
  exit /b %RC%
)

echo.
echo Setup completed successfully.
echo Vidja_ComfyUI_Ready.zip should now exist if the GPU smoke test passed.
pause
exit /b 0

:bootstrap_python
set "BOOT=%~dp0python_bootstrap"
if exist "%BOOT%\python.exe" exit /b 0
mkdir "%BOOT%" 2>nul
set "URL=https://www.python.org/ftp/python/3.13.7/python-3.13.7-embed-amd64.zip"
set "ZIP=%TEMP%\vidja_py313.zip"
echo Downloading Python embeddable 3.13...
powershell -NoProfile -Command "try { Invoke-WebRequest -Uri '%URL%' -OutFile '%ZIP%' -UseBasicParsing } catch { exit 1 }"
if errorlevel 1 (
  echo Failed to download Python embeddable.
  exit /b 1
)
powershell -NoProfile -Command "Expand-Archive -Path '%ZIP%' -DestinationPath '%BOOT%' -Force"
if errorlevel 1 exit /b 1
REM Enable site packages for embeddable distribution
if exist "%BOOT%\python313._pth" (
  powershell -NoProfile -Command "(Get-Content '%BOOT%\python313._pth') -replace '#import site','import site' | Set-Content '%BOOT%\python313._pth'"
)
"%BOOT%\python.exe" -m ensurepip --upgrade >nul 2>&1
"%BOOT%\python.exe" -m pip install --upgrade pip >nul 2>&1
exit /b 0
