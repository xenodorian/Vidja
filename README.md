# Vidja: Build a Self-Contained ComfyUI Video Generator

## Objective

The objective of this repository is to produce **one Windows ZIP file that can be extracted and run locally to generate video with ComfyUI**, without requiring you to manually install Python, ComfyUI, custom nodes, or model files.

The target configuration is an NVIDIA RTX 3060 12GB with 32 GB RAM.

The intended final package must contain:

- ComfyUI
- A portable Python/runtime environment
- Required dependencies
- ComfyUI-GGUF
- The required Wan 2.1 model files
- A working Wan 2.1 text-to-video workflow
- Windows launch/setup scripts
- Documentation
- No dependence on the developer's original machine paths

**Important:** The project is not complete until the packaged workflow has actually generated a playable video on the target hardware.

---

## Current Workflow

The initial target is:

**Wan 2.1 T2V 1.3B**

The workflow uses:

- Wan 2.1 T2V 1.3B GGUF, Q4_K_S
- UMT5 XXL GGUF, Q3_K_S
- Wan 2.1 VAE
- ComfyUI-GGUF
- 832x480 output
- 33 frames
- 16 FPS
- 30 sampling steps
- CFG 6

The workflow is:

```
Text prompt
    ↓
UMT5 text encoder
    ↓
Wan 2.1 T2V 1.3B
    ↓
KSampler
    ↓
Wan VAE
    ↓
Video
```

The workflow file is:

`workflows/wan2.1_t2v_1.3b_gguf_3060.json`

The current workflow has **not yet been proven end-to-end on an RTX 3060**. Do not treat the presence of the JSON as proof that generation works.

---

# What You Need To Do

The fastest path to the final ZIP is:

1. Prepare the Windows machine.
2. Run the Vidja setup script.
3. Let it download the ComfyUI runtime and model files.
4. Start ComfyUI.
5. Load the included Wan workflow.
6. Generate a short test video.
7. Fix any errors.
8. Repeat until a real video is produced.
9. Run the packaging script.
10. Extract the resulting ZIP into a separate directory and test it again.
11. Only then consider the package complete.

---

# Step 1: Get the Repository

Clone or download this repository onto the Windows machine that will actually run the model.

The repository is:

`https://github.com/xenodorian/Vidja`

Do not put the final runtime inside an existing ComfyUI installation. The goal is to create a self-contained Vidja distribution.

---

# Step 2: Run the Automated Setup

The intended setup script is:

`Setup_Vidja_Windows.bat`

Run it from Windows.

It is designed to:

1. Download the official NVIDIA portable ComfyUI distribution.
2. Extract the portable runtime.
3. Copy the Vidja ComfyUI source and project files into it.
4. Install ComfyUI-GGUF requirements.
5. Download the Wan 2.1 diffusion model.
6. Download the UMT5 XXL text encoder.
7. Download the Wan VAE.
8. Place each file in the correct ComfyUI model directory.

The expected model locations are:

```
ComfyUI/
├── models/
│   ├── unet/
│   │   └── Wan2.1-T2V-1.3B-Q4_K_S.gguf
│   ├── clip/
│   │   └── umt5-xxl-encoder-Q3_K_S.gguf
│   └── vae/
│       └── wan_2.1_vae.safetensors
└── custom_nodes/
    └── ComfyUI-GGUF/
```

If setup fails, **do not skip the error**. Record the complete error message in `Current_Work.md`.

---

# Step 3: Start ComfyUI

The portable installation should contain the NVIDIA launcher supplied by ComfyUI.

Start it with:

`run_nvidia_gpu.bat`

Do not install a separate Python version unless the existing portable runtime fails and the failure specifically requires it.

The first verification is simply that ComfyUI starts without Python, CUDA, or custom-node import errors.

If ComfyUI starts, open the local web interface it reports in the console.

---

# Step 4: Verify ComfyUI-GGUF

Before attempting generation, verify that the custom node loads.

The workflow requires these node types:

- `UnetLoaderGGUF`
- `CLIPLoaderGGUF`

If either node is reported as missing, stop and fix the custom-node installation before testing the workflow.

Do not replace the GGUF nodes with ordinary checkpoint loaders unless the workflow and model format are deliberately changed and retested.

---

# Step 5: Verify the Models

The following three files must exist before running the workflow:

```
models/unet/Wan2.1-T2V-1.3B-Q4_K_S.gguf
models/clip/umt5-xxl-encoder-Q3_K_S.gguf
models/vae/wan_2.1_vae.safetensors
```

The workflow should show these files in its model selectors.

If a model is missing:

1. Check the filename.
2. Check the directory.
3. Restart ComfyUI.
4. Check the console for model-loading errors.

Do not rename model files merely to make the selector display them.

---

# Step 6: Load the Included Workflow

In ComfyUI, load:

`workflows/wan2.1_t2v_1.3b_gguf_3060.json`

The graph should contain:

- GGUF diffusion model loader
- GGUF UMT5 loader
- Wan VAE loader
- Positive prompt
- Negative prompt
- Video latent
- KSampler
- Video creation
- Video save

The initial settings are deliberately conservative for the RTX 3060 target.

---

# Step 7: Run a Short Test First

Do not immediately spend a long time rendering the full configured output.

First reduce the video length to a small test, if necessary.

For example, reduce the frame count in the video latent node to approximately 17 frames.

Use a simple prompt such as:

```
a red ball rolling across a wooden table, fixed camera, realistic motion
```

Queue the workflow.

The first successful test must demonstrate all of the following:

- The GGUF diffusion model loads.
- The UMT5 encoder loads.
- Sampling completes.
- The VAE decodes successfully.
- Video creation completes.
- A video file is written.
- The resulting video can actually be opened and played.

A workflow that merely reaches the end of the node graph without producing a playable file does not count as success.

---

# Step 8: If It Runs Out Of VRAM

The RTX 3060 has 12 GB of VRAM.

If the workflow produces a CUDA out-of-memory error:

1. Record the exact error.
2. Reduce the frame count.
3. Retry.
4. If necessary, reduce resolution.
5. Retry.
6. Only change model quantization after the simpler changes have been tested.

Do not immediately replace the entire workflow.

The purpose of the first successful run is to establish a known working baseline.

Once a baseline works, increase the frame count and resolution toward the configured 832x480 / 33-frame target.

Record the highest settings that successfully work.

---

# Step 9: If the Workflow Fails

When something fails, use this procedure:

### Missing node

Check:

`custom_nodes/ComfyUI-GGUF`

Then restart ComfyUI.

### Missing model

Check the exact model filename and directory.

### CUDA error

Record the complete console error and determine whether it is:

- VRAM exhaustion
- incompatible CUDA/PyTorch
- unsupported GPU operation
- driver failure

### Python/import error

Record the complete traceback.

Do not randomly install packages into the system Python. The final package must remain portable.

### Workflow/node error

Record:

- Node name
- Error text
- Input values
- ComfyUI version
- Custom-node version

Then fix the smallest component necessary and rerun the test.

Every failed attempt that changes the project should be recorded in `Current_Work.md`.

---

# Step 10: Prove the Runtime Is Portable

After a successful generation, do not immediately create the final ZIP.

First test the runtime from a different directory.

For example:

```
C:\VidjaTest\
```

Copy/extract the complete prepared runtime there.

Launch it from that location.

Verify that it does not depend on:

- The original project directory
- Your user profile
- A separate Python installation
- A separate ComfyUI installation
- Developer-specific absolute paths
- Files outside the package

Then run the workflow again.

This second generation is the portability test.

---

# Step 11: Package the Final ZIP

Once the workflow has successfully generated video and the extracted copy has also generated video, run:

`Package_Vidja.bat`

The intended output is:

`Vidja_ComfyUI_Ready.zip`

The ZIP must contain the complete tested runtime, not merely the Git repository.

It must include:

```
ComfyUI/
models/
custom_nodes/
workflows/
launcher/setup files
documentation
Current_Work.md
```

It must also include the actual model files.

Do not create a ZIP that merely downloads the models later and call it the completed deliverable.

---

# Step 12: Final Clean Extraction Test

Before declaring success:

1. Create a completely new directory.
2. Extract `Vidja_ComfyUI_Ready.zip`.
3. Launch it using the included launcher.
4. Open the included workflow.
5. Generate a video.
6. Open the resulting video.
7. Confirm that no files outside the extracted package were required.

Only after this test should `Current_Work.md` mark the project complete.

---

# Files Used By This Project

The important project files are:

```
Current_Work.md
workflows/wan2.1_t2v_1.3b_gguf_3060.json
Setup_Vidja_Windows.bat
Package_Vidja.bat
```

If the setup or packaging BAT files are missing from the repository, restore them before attempting the final packaging stage. They are part of the intended automated build process.

---

# Model Sources

The current workflow was built around these model sources:

Wan 2.1 T2V 1.3B GGUF:

`https://huggingface.co/samuelchristlie/Wan2.1-T2V-1.3B-GGUF`

UMT5 XXL GGUF:

`https://huggingface.co/city96/umt5-xxl-encoder-gguf`

Wan 2.1 VAE:

`https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged`

GGUF custom node:

`https://github.com/city96/ComfyUI-GGUF`

Official ComfyUI:

`https://github.com/Comfy-Org/ComfyUI`

These sources are listed so that a failed download can be diagnosed and reproduced.

---

# What Counts As Completion

The objective is complete only when all of these are true:

- [ ] ComfyUI starts from the packaged runtime.
- [ ] ComfyUI-GGUF loads without errors.
- [ ] All required model files are present.
- [ ] The included workflow loads without missing nodes.
- [ ] The workflow successfully generates a video.
- [ ] The generated video is playable.
- [ ] The packaged copy works from a new directory.
- [ ] The final ZIP contains the actual runtime and models.
- [ ] The final ZIP works without relying on the development directory.
- [ ] `Current_Work.md` records the successful test and final ZIP size/location.

Do not mark any unchecked item complete based on assumption.

---

# Handoff Rule

If work stops before completion, update `Current_Work.md` with:

1. What was completed.
2. What failed.
3. The exact error.
4. What was changed.
5. What remains.
6. The exact next command or action.

The next AI should read `Current_Work.md` first, inspect the repository second, and continue from the first incomplete item.

The end goal is not a source repository.

**The end goal is a tested, self-contained Windows ZIP that can be extracted and used to generate video.**
