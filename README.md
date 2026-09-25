# Vidja

This repository exists for one purpose:

**Run Wan 2.1 text-to-video locally on my NVIDIA RTX 3060 12GB using a self-contained ComfyUI package.**

## Setup

Download or clone this repository, then run:

`Setup_Vidja_Windows.bat`

That is the entire setup process.

The script automatically:

- Downloads the Windows NVIDIA ComfyUI portable runtime.
- Downloads an isolated Python bootstrap if needed.
- Installs ComfyUI-GGUF.
- Downloads and verifies the required Wan 2.1 models.
- Installs the included workflow.
- Starts ComfyUI.
- Runs a GPU generation test.
- Verifies that a video was produced.
- Creates `Vidja_ComfyUI_Ready.zip`.
- Opens ComfyUI in the browser.

Do not manually install Python, ComfyUI, PyTorch, CUDA, ComfyUI-GGUF, or the models.

## Workflow

`workflows/wan2.1_t2v_1.3b_gguf_3060.json`

Target configuration:

- Wan 2.1 T2V 1.3B
- GGUF Q4_K_S
- UMT5 XXL GGUF Q3_K_S
- Wan 2.1 VAE
- 832x480
- 33 frames
- 16 FPS
- 30 steps
- CFG 6

The automatic setup test uses 9 frames and 4 steps to verify the complete GPU pipeline before attempting the full configuration.

## If setup fails

Keep:

`Vidja_Setup.log`
`Vidja_ComfyUI.log`

Record the exact failure in:

`Current_Work.md`

## Final package

After the GPU test succeeds, the script creates:

`Vidja_ComfyUI_Ready.zip`

The ZIP is intended to contain the complete working runtime and actual model files.

The project is finished only after that ZIP has been extracted into a clean directory and successfully used to generate a playable video.

## Current state

The automated setup and workflow are in the repository.

The final hardware test has not been performed from this development environment because it does not provide an NVIDIA GPU. The first real generation test occurs when `Setup_Vidja_Windows.bat` is run on the target Windows/NVIDIA machine.

The project deliberately uses ComfyUI's current Windows portable NVIDIA runtime, which officially supports NVIDIA 20-series and newer GPUs.