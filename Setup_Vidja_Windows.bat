@echo off
setlocal EnableExtensions EnableDelayedExpansion

rem Vidja ComfyUI automated Windows setup
rem Target: NVIDIA RTX 20-series or newer, including RTX 3060.
rem This script downloads the official ComfyUI portable runtime and the exact
rem model assets selected for the bundled Wan 2.1 T2V 1.3B GGUF workflow.

set "ROOT=%~dp0"
set "DOWNLOADS=%ROOT%_downloads"
set "PORTABLE=%ROOT%Vidja_Portable"
set "ARCHIVE=%DOWNLOADS%\ComfyUI_windows_portable_nvidia.7z"
set "RUNTIME_URL=https://github.com/Comfy-Org/ComfyUI/releases/latest/download/ComfyUI_windows_portable_nvidia.7z"
set "WAN_URL=https://huggingface.co/samuelchristlie/Wan2.1-T2V-1.3B-GGUF/resolve/main/Wan2.1-T2V-1.3B-Q4_K_S.gguf?download=true"
set "T5_URL=https://huggingface.co/city96/umt5-xxl-encoder-gguf/resolve/main/umt5-xxl-encoder-Q3_K_S.gguf?download=true"
set "VAE_URL=https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/vae/wan_2.1_vae.safetensors?download=true"

if not exist "%DOWNLOADS%" mkdir "%DOWNLOADS%"
if not exist "%PORTABLE%" mkdir "%PORTABLE%"

echo.
echo === Vidja ComfyUI Setup ===
echo.

if not exist "%ARCHIVE%" (
    echo Downloading official ComfyUI NVIDIA portable runtime...
    curl.exe -L --fail --retry 5 --retry-delay 3 --continue-at - -o "%ARCHIVE%" "%RUNTIME_URL%"
    if errorlevel 1 goto :download_failed
)

if not exist "%PORTABLE%\python_embeded\python.exe" (
    echo Extracting portable runtime...
    tar -xf "%ARCHIVE%" -C "%PORTABLE%"
    if errorlevel 1 goto :extract_failed
)

if not exist "%PORTABLE%\ComfyUI\main.py" goto :runtime_failed

echo Copying the Vidja ComfyUI source into the portable runtime...
robocopy "%ROOT%" "%PORTABLE%\ComfyUI" /E /XD ".git" ".github" "_downloads" "Vidja_Portable" /XF "Setup_Vidja_Windows.bat" "Package_Vidja.bat" >nul
if errorlevel 8 goto :copy_failed

echo Installing ComfyUI-GGUF dependencies...
"%PORTABLE%\python_embeded\python.exe" -m pip install -r "%PORTABLE%\ComfyUI\custom_nodes\ComfyUI-GGUF\requirements.txt"
if errorlevel 1 goto :pip_failed

if not exist "%PORTABLE%\ComfyUI\models\unet" mkdir "%PORTABLE%\ComfyUI\models\unet"
if not exist "%PORTABLE%\ComfyUI\models\clip" mkdir "%PORTABLE%\ComfyUI\models\clip"
if not exist "%PORTABLE%\ComfyUI\models\vae" mkdir "%PORTABLE%\ComfyUI\models\vae"

call :download_asset "%WAN_URL%" "%PORTABLE%\ComfyUI\models\unet\Wan2.1-T2V-1.3B-Q4_K_S.gguf" "Wan 2.1 T2V 1.3B Q4_K_S"
if errorlevel 1 goto :download_failed

call :download_asset "%T5_URL%" "%PORTABLE%\ComfyUI\models\clip\umt5-xxl-encoder-Q3_K_S.gguf" "UMT5 XXL Q3_K_S"
if errorlevel 1 goto :download_failed

call :download_asset "%VAE_URL%" "%PORTABLE%\ComfyUI\models\vae\wan_2.1_vae.safetensors" "Wan 2.1 VAE"
if errorlevel 1 goto :download_failed

echo.
echo Setup complete.
echo.
echo Launch with:
echo   %PORTABLE%\run_nvidia_gpu.bat
echo.
echo The included workflow is:
echo   %PORTABLE%\ComfyUI\workflows\wan2.1_t2v_1.3b_gguf_3060.json
echo.
exit /b 0

:download_asset
set "URL=%~1"
set "DEST=%~2"
set "LABEL=%~3"
if exist "%DEST%" (
    echo %LABEL% already present.
    exit /b 0
)
echo Downloading %LABEL%...
curl.exe -L --fail --retry 5 --retry-delay 3 --continue-at - -o "%DEST%.partial" "%URL%"
if errorlevel 1 exit /b 1
move /Y "%DEST%.partial" "%DEST%" >nul
if errorlevel 1 exit /b 1
exit /b 0

:download_failed
echo ERROR: A download failed. Check the network connection and rerun this script.
exit /b 1

:extract_failed
echo ERROR: The portable runtime could not be extracted.
exit /b 1

:runtime_failed
echo ERROR: The extracted portable runtime is incomplete.
exit /b 1

:copy_failed
echo ERROR: Could not copy the Vidja source into the portable runtime.
exit /b 1

:pip_failed
echo ERROR: Could not install the ComfyUI-GGUF Python dependencies.
exit /b 1
