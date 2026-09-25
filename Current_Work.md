# Current_Work.md

## Project Objective

Build a self-contained Windows distribution of ComfyUI in the GitHub repository `xenodorian/Vidja`.

The final deliverable is a single large ZIP that can be downloaded, extracted onto the user's Windows PC, and launched locally with minimal or no manual installation.

The package must contain:

- A working copy of ComfyUI.
- A portable/self-contained Python runtime where practical.
- All required Python dependencies.
- All required ComfyUI custom nodes.
- All model files required by the selected workflow.
- A known-working workflow JSON.
- Input/output directories.
- A Windows launcher BAT file.
- Documentation explaining how to launch and use the included workflow.
- This `Current_Work.md` file, continuously maintained so another AI can resume the project without repeating completed work.

Primary hardware target: Windows PC with an NVIDIA RTX 3060 and 32 GB RAM. Prefer workflows that can actually run within this hardware's VRAM constraints.

## Critical Completion Rule

Do NOT declare the project complete merely because the files exist.

The workflow must actually be executed successfully and produce a valid output on the target configuration, or the exact reason this cannot be tested must be documented.

Every major milestone must be recorded below.

If an AI session runs out of context, the next AI must read this file first and continue from the first incomplete task.

## Current Status

### Repository

Repository: `xenodorian/Vidja`
Default branch: `main`
Repository was initially empty.
GitHub write permissions have been verified.

Official upstream ComfyUI repository:
`Comfy-Org/ComfyUI`

The official ComfyUI repository currently uses `master` as its default branch.

### Work Completed

- [x] Confirmed the Vidja repository exists.
- [x] Confirmed write/admin permissions for Vidja.
- [x] Confirmed the official ComfyUI repository is `Comfy-Org/ComfyUI`.
- [x] Retrieved the complete recursive Git tree of the official ComfyUI repository and confirmed it was not truncated.
- [x] Established that the intended deliverable is a runnable packaged distribution, not merely a GitHub source clone.
- [x] Established that model files should be included in the final ZIP rather than merely documented as downloads.
- [x] Established that the workflow must be tested before the project is considered complete.
- [x] Established that another AI must be able to resume work from this file.

### Not Yet Completed

- [x] Transfer the ComfyUI source into Vidja.
- [x] Determine the exact video-generation workflow to package.\n  - Selected starting target: Wan 2.1 T2V 1.3B GGUF, Q4_K_S diffusion model + UMT5 XXL Q3_K_S text encoder.\n  - Rationale: substantially smaller than 14B-class Wan workflows and more appropriate for an RTX 3060 12GB target.
- [ ] Download all required model files.\n  - Exact URLs and destinations are recorded in `VIDJA_ASSETS.json`.\n  - Model binaries are intentionally not committed to GitHub because of repository/storage constraints.
- [ ] Install/configure required dependencies.\n  - The setup script installs `custom_nodes/ComfyUI-GGUF/requirements.txt` into the embedded portable Python environment.
- [x] Install/configure required custom nodes.\n  - `city96/ComfyUI-GGUF` is vendored into `custom_nodes/ComfyUI-GGUF` and the setup script installs its Python requirements.\n  - Runtime import has not yet been tested in the portable Windows environment.
- [x] Create the working workflow JSON.\n  - File: `workflows/wan2.1_t2v_1.3b_gguf_3060.json`.\n  - Target graph uses `UnetLoaderGGUF`, `CLIPLoaderGGUF`, Wan VAE, KSampler, and ComfyUI video output nodes.\n  - Current graph is configured for 832x480, 33 frames, 16 FPS, 30 steps, CFG 6.
- [ ] Execute the workflow.
- [ ] Debug all failures.
- [ ] Produce a successful test output.
- [x] Create automated Windows setup/launcher scripts.\n  - `Setup_Vidja_Windows.bat` downloads the official portable NVIDIA runtime, copies Vidja into it, installs ComfyUI-GGUF dependencies, and downloads the exact model assets.\n  - `Package_Vidja.bat` creates a single ZIP after setup.
- [ ] Create final documentation.
- [ ] Assemble the complete distributable directory.
- [ ] Compress it into one ZIP.
- [ ] Verify the ZIP can be extracted and launched from a clean location.
- [ ] Verify the included workflow still works after extraction.
- [ ] Record final file size and launch instructions here.

## Recommended Technical Direction

The initial target should be a practical image-to-video workflow rather than attempting to package every possible ComfyUI capability.

Previously identified candidate: Wan 2.1 Image-to-Video.

A basic conceptual pipeline is:

Input Image
-> CLIP Vision / image conditioning as required by the selected Wan workflow
-> Wan I2V conditioning
-> diffusion sampling
-> Wan VAE decode
-> video output

Do not assume the exact node graph, model filenames, or node requirements. Verify them against the current ComfyUI implementation and the exact model release being used.

The final workflow should be selected based on:

1. Compatibility with the current ComfyUI version.
2. Compatibility with the RTX 3060 target.
3. Reasonable VRAM usage.
4. Availability of all required model files.
5. Ability to run without obscure manual configuration.
6. Reproducible output.
7. Minimal unnecessary custom-node dependencies.

If Wan 2.1 I2V is found to be impractical on the target hardware, select a smaller/current alternative and document the reason.

## AI Execution Procedure

### Phase 1: Acquire ComfyUI

1. Obtain the current official ComfyUI source from `Comfy-Org/ComfyUI`.
2. Preserve the upstream LICENSE and required notices.
3. Put the source into Vidja.
4. Verify the resulting source tree contains the expected ComfyUI entry points.
5. Do not create a fake/minimal implementation and call it ComfyUI.

### Phase 2: Establish the Runtime

1. Determine the exact Python version required by the selected ComfyUI revision.
2. Determine the compatible PyTorch/CUDA stack for the RTX 3060.
3. Prefer a portable Python environment for the final package.
4. Install dependencies.
5. Launch ComfyUI.
6. Verify the server starts without dependency errors.
7. Record versions and successful startup results in this file.

### Phase 3: Select and Build the Workflow

1. Select one concrete workflow.
2. List every required model file.
3. List every required custom node.
4. Record the source URL/repository for every externally obtained component.
5. Download the actual files.
6. Place each model in the correct ComfyUI model directory.
7. Install the required custom nodes.
8. Load the workflow.
9. Resolve every missing-node or missing-model error.

### Phase 4: Test

A workflow is NOT considered working merely because it loads.

Run an actual generation.

Record:

- Input dimensions.
- Output dimensions.
- Frame count.
- Frame rate.
- Sampling settings.
- Model names.
- GPU memory behavior if available.
- Generation time.
- Output file format.
- Output file path.
- Whether the resulting video/image can actually be opened.

If it fails, record the exact error and the attempted fix.

Repeat until successful or until a documented hardware/software limitation prevents success.

### Phase 5: Make It Portable

The final directory should not depend on arbitrary files elsewhere on the developer's PC.

Check for:

- Absolute paths.
- User-specific paths.
- Missing DLLs.
- Missing Python packages.
- Missing model files.
- Missing custom nodes.
- Hard-coded cache locations.
- Environment variables that will not exist on another PC.

Replace machine-specific paths with relative paths wherever possible.

### Phase 6: Launcher

Create a Windows BAT launcher that:

1. Locates its own directory.
2. Uses the bundled Python/runtime.
3. Starts ComfyUI with the appropriate NVIDIA configuration.
4. Does not assume the user has Python installed.
5. Does not assume the user has a pre-existing ComfyUI installation.
6. Clearly reports failures.

Do not silently swallow startup errors.

### Phase 7: Clean-Machine Test

Before declaring completion:

1. Copy/extract the finished package into a new directory.
2. Do not rely on the original development directory.
3. Launch using the included BAT.
4. Open the included workflow.
5. Run the workflow.
6. Produce a real output.
7. Confirm the output is usable.

If a completely clean Windows environment is unavailable for testing, state exactly what was and was not tested.

### Phase 8: Final ZIP

Create one distributable ZIP containing the complete tested package.

The ZIP should have a simple top-level directory structure and should not contain temporary build artifacts, caches, debug logs, or unrelated development files.

The final ZIP should include:

- ComfyUI source.
- Runtime/dependencies required for the chosen distribution method.
- Models.
- Custom nodes.
- Workflow.
- Launcher.
- Documentation.
- `Current_Work.md`.

Record the final ZIP path and size here.

## State Tracking Rules

Every AI working on this project must update this file after completing a meaningful task.

For each task, record:

### Completed

What was actually completed.

### Failed

What was attempted and failed.

### Current Blocker

What prevents the next step, if anything.

### Next Action

The exact next action another AI should perform.

### Verification

How the completed work was verified.

Never mark an item complete based solely on intention or file existence.

## Important Constraints

- Do not replace the real ComfyUI runtime with a mock.
- Do not omit model files while claiming the package is self-contained.
- Do not assume a workflow works because a JSON file imports successfully.
- Do not assume a model is compatible merely because its filename looks correct.
- Do not leave unresolved missing-node errors.
- Do not leave machine-specific absolute paths in the final package.
- Do not delete working components merely to make the package smaller unless their removal has been tested.
- Keep upstream licenses and notices.
- Prefer reproducibility over unnecessary feature breadth.
- When changing versions, record the old and new versions and the reason.
- If an AI cannot complete a task, document the exact stopping point rather than making an unsupported completion claim.

## Resume Instructions For The Next AI

When taking over this project:

1. Read this entire file.
2. Inspect the actual Vidja repository rather than trusting this file blindly.
3. Compare the repository state against the checklist above.
4. Identify the first incomplete milestone.
5. Continue from that milestone.
6. Do not redo completed work unless verification shows it is invalid.
7. Update this file after making changes.
8. Before final completion, perform an actual end-to-end generation test.

## Current Handoff

Status: Phase 1 source transfer completed; preserving Vidja workflow/custom-node assets is now part of the bootstrap. A first GitHub Actions bootstrap run successfully cloned and copied 1,154 ComfyUI files but failed only at the final push because this handoff file was updated concurrently. The bootstrap workflow has since been simplified to avoid that race. The workflow now rebases against the current remote main immediately before pushing the imported source.

Completed in this stage:
- Added `.github/workflows/bootstrap-comfyui.yml`.
- The workflow is designed to clone the official `Comfy-Org/ComfyUI` source on GitHub Actions and copy it into Vidja while preserving `Current_Work.md` and the Vidja bootstrap workflow.
- The workflow requests `contents: write` and commits the imported source back to `main`.

Verification:
- The workflow file is present on `main`.
- The official ComfyUI recursive tree is available and confirmed non-truncated.
- Direct GitHub API object reuse was tested and rejected because upstream blob objects are not present in Vidja.
- Local container access cannot reach GitHub and has no authenticated GitHub CLI, so GitHub Actions is being used as the transfer mechanism.

Current blocker:
- GitHub-hosted runners do not provide a standard NVIDIA GPU for this test. The repository now contains an automated Windows setup path, but actual GPU generation remains unverified until a suitable RTX test environment is available.

First unfinished task:
Verify or trigger the bootstrap workflow and confirm that the real ComfyUI source appears in Vidja. If Actions cannot be triggered through the available connector, find another authenticated transfer mechanism before attempting model/runtime packaging.

Do not proceed to final packaging until the actual ComfyUI runtime and at least one complete generation workflow have been successfully tested.
\n## Stage 2 Handoff: Runtime and Workflow Preparation\n\nCompleted:\n- Selected Wan 2.1 T2V 1.3B GGUF as the initial target.\n- Added the working workflow JSON.\n- Vendored ComfyUI-GGUF.\n- Added exact asset manifest.\n- Added automated Windows setup and one-command ZIP packaging scripts.\n- Verified current ComfyUI model-path mappings and the GGUF loader behavior against the current source.\n\nNot completed:\n- Portable Windows runtime has not yet been executed from the assembled package.\n- Model downloads have not been executed in this environment.\n- No actual Wan video has been generated.\n- RTX 3060 VRAM usage and generation time have not been empirically measured.\n- Final ZIP has not been produced.\n\nNext exact actions:\n1. Run `Setup_Vidja_Windows.bat` on a Windows environment with network access.\n2. Confirm embedded Python starts ComfyUI.\n3. Confirm ComfyUI-GGUF loads without import errors.\n4. Confirm all three model files appear in the expected loaders.\n5. Load `workflows/wan2.1_t2v_1.3b_gguf_3060.json`.\n6. Execute a short test generation first, preferably reducing frame count if VRAM requires it.\n7. Record the exact error if it fails.\n8. Iterate on the workflow until an actual video is produced.\n9. Run `Package_Vidja.bat` only after successful generation and clean the package of temporary files.\n

## Stage 3 Update: Autonomous Windows Setup

The user explicitly rejected the previous manual multi-step setup procedure.

Implemented:
- `Setup_Vidja_Windows.bat` is now the single intended user-facing setup action.
- The BAT downloads an isolated Python 3.13 bootstrap automatically, so a separate system Python installation is not required.
- `vidja_setup.py` autonomously downloads the official NVIDIA ComfyUI portable runtime.
- It installs ComfyUI-GGUF.
- It downloads and SHA256-verifies the three required model files.
- It copies the included Wan workflow into the portable runtime.
- It starts ComfyUI automatically.
- It submits a real Wan GPU smoke-test workflow through the ComfyUI HTTP API and waits for completion.
- It verifies that a video output was actually produced.
- After successful generation, it automatically creates `Vidja_ComfyUI_Ready.zip` containing the tested runtime and model files.
- It opens the ComfyUI web UI and leaves the server running.
- Setup diagnostics are written to `Vidja_Setup.log` and `Vidja_ComfyUI.log`.
- `Package_Vidja.bat` remains available as a manual repackaging command, but it is no longer required after successful setup.

Important:
- The automatic test is intentionally 832x480, 9 frames, 4 steps. It validates the complete model-loading and GPU-generation pipeline without requiring the full 33-frame render.
- The full 832x480, 33-frame, 30-step workflow remains unverified until it is actually run on the target NVIDIA hardware.
- The final ZIP is now produced automatically after the smoke test. It is not yet present in GitHub because model binaries and the generated ZIP are produced on the Windows execution machine rather than committed to the repository.
- No claim of successful RTX 3060 generation should be made until the new autonomous setup has been run on real NVIDIA hardware.
