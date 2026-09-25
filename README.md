# Vidja

Vidja is a self-contained Windows ComfyUI video generator targeting an NVIDIA RTX 3060 12GB.

## One-step setup

Download or clone this repository on the Windows machine that will run the generator.

Then run:

`Setup_Vidja_Windows.bat`

That is the intended user-facing setup procedure.

The setup program autonomously:

1. Downloads an isolated Python bootstrap if necessary.
2. Downloads the official NVIDIA ComfyUI portable runtime.
3. Extracts the runtime.
4. Installs ComfyUI-GGUF.
5. Downloads the Wan 2.1 T2V 1.3B GGUF model.
6. Downloads the UMT5 XXL GGUF text encoder.
7. Downloads the Wan 2.1 VAE.
8. Verifies the downloaded model hashes.
9. Copies the included workflow into the runtime.
10. Starts ComfyUI.
11. Submits an automatic Wan GPU smoke test through the ComfyUI API.
12. Waits for generation to finish and verifies that a video file was produced.
13. Opens the ComfyUI web interface.

There should be no need to manually install Python, ComfyUI, custom nodes, or the models.

The setup logs are written to:

`Vidja_Setup.log`
`Vidja_ComfyUI.log`

## Target workflow

The included workflow is:

`workflows/wan2.1_t2v_1.3b_gguf_3060.json`

It uses:

- Wan 2.1 T2V 1.3B GGUF Q4_K_S
- UMT5 XXL GGUF Q3_K_S
- Wan 2.1 VAE
- ComfyUI-GGUF
- 832x480
- 33 frames
- 16 FPS
- 30 sampling steps
- CFG 6

The automatic setup test intentionally uses a much shorter 9-frame, 4-step generation. This establishes that the runtime, custom node, models, CUDA execution, VAE decode, video encoding, and output path work before the user attempts the full workflow.

The setup script does not claim that the full 33-frame configuration has been benchmarked until that configuration is actually tested.

## Final package

After a successful setup and any required tuning, the project can be packaged with:

`Package_Vidja.bat`

The desired final artifact is:

`Vidja_ComfyUI_Ready.zip`

That ZIP must contain the actual runtime and model files. A ZIP that merely downloads models later is not the completed deliverable.

## Important

The current development environment cannot perform the final RTX 3060 GPU generation itself. The first real hardware validation therefore occurs when `Setup_Vidja_Windows.bat` is run on a Windows NVIDIA machine.

If the automatic test fails, preserve:

- `Vidja_Setup.log`
- `Vidja_ComfyUI.log`

and record the failure in `Current_Work.md`.

The project is complete only after a real generated video has been produced and the packaged runtime has been tested from a clean extraction directory.
