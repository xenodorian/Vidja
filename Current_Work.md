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

- [ ] Transfer the ComfyUI source into Vidja.
- [ ] Determine the exact video-generation workflow to package.
- [ ] Download all required model files.
- [ ] Install/configure required dependencies.
- [ ] Install/configure required custom nodes.
- [ ] Create the working workflow JSON.
- [ ] Execute the workflow.
- [ ] Debug all failures.
- [ ] Produce a successful test output.
- [ ] Create the Windows launcher.
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

Status: Phase 1 bootstrap automation added.

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
- The repository currently reports zero GitHub Actions workflow runs. The bootstrap workflow therefore has not yet been verified as executing.

First unfinished task:
Verify or trigger the bootstrap workflow and confirm that the real ComfyUI source appears in Vidja. If Actions cannot be triggered through the available connector, find another authenticated transfer mechanism before attempting model/runtime packaging.

Do not proceed to final packaging until the actual ComfyUI runtime and at least one complete generation workflow have been successfully tested.
