#!/usr/bin/env python3
"""
Vidja autonomous Windows setup.

Downloads the official ComfyUI NVIDIA portable runtime, installs ComfyUI-GGUF,
downloads and verifies the Wan 2.1 models listed in VIDJA_ASSETS.json, installs
the included workflow, starts ComfyUI, runs a short GPU smoke test, verifies
video output, and packages Vidja_ComfyUI_Ready.zip.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LOG = ROOT / "Vidja_Setup.log"
COMFY_LOG = ROOT / "Vidja_ComfyUI.log"
ASSETS_PATH = ROOT / "VIDJA_ASSETS.json"
PORTABLE_DIR = ROOT / "ComfyUI_windows_portable"
WORKFLOW_SRC = ROOT / "workflows" / "wan2.1_t2v_1.3b_gguf_3060.json"
GGUF_SRC = ROOT / "custom_nodes" / "ComfyUI-GGUF"
READY_ZIP = ROOT / "Vidja_ComfyUI_Ready.zip"
COMFY_HOST = "127.0.0.1"
COMFY_PORT = 8188


def log(msg: str) -> None:
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def die(msg: str, code: int = 1) -> None:
    log(f"FATAL: {msg}")
    sys.exit(code)


def load_assets() -> dict:
    if not ASSETS_PATH.is_file():
        die(f"Missing {ASSETS_PATH}")
    return json.loads(ASSETS_PATH.read_text(encoding="utf-8"))


def download(url: str, dest: Path, desc: str) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.is_file() and dest.stat().st_size > 0:
        log(f"Already present: {dest.name} ({dest.stat().st_size} bytes)")
        return
    log(f"Downloading {desc}: {url}")
    tmp = dest.with_suffix(dest.suffix + ".partial")
    try:
        with urllib.request.urlopen(url, timeout=600) as resp, tmp.open("wb") as out:
            total = int(resp.headers.get("Content-Length") or 0)
            done = 0
            while True:
                chunk = resp.read(1024 * 1024)
                if not chunk:
                    break
                out.write(chunk)
                done += len(chunk)
                if total and done % (50 * 1024 * 1024) < 1024 * 1024:
                    pct = 100.0 * done / total
                    log(f"  {desc}: {done // (1024*1024)} MB / {total // (1024*1024)} MB ({pct:.0f}%)")
        tmp.replace(dest)
        log(f"Saved {dest} ({dest.stat().st_size} bytes)")
    except Exception as e:
        if tmp.exists():
            tmp.unlink(missing_ok=True)
        die(f"Download failed for {desc}: {e}")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def find_7z() -> str | None:
    """Locate 7z/7za/7zr on PATH, common install dirs, or a local tools copy."""
    for name in ("7z", "7z.exe", "7za", "7za.exe", "7zr", "7zr.exe"):
        found = shutil.which(name)
        if found:
            return found
    candidates = [
        Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "7-Zip" / "7z.exe",
        Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / "7-Zip" / "7z.exe",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "7-Zip" / "7z.exe",
        ROOT / "tools" / "7zr.exe",
        ROOT / "tools" / "7za.exe",
        ROOT / "tools" / "7z.exe",
    ]
    for p in candidates:
        if p and p.is_file():
            return str(p)
    return None


def ensure_7zr() -> str:
    """Return path to a usable 7z binary, downloading standalone 7zr.exe if needed."""
    existing = find_7z()
    if existing:
        return existing
    tools = ROOT / "tools"
    tools.mkdir(parents=True, exist_ok=True)
    dest = tools / "7zr.exe"
    url = "https://www.7-zip.org/a/7zr.exe"
    log(f"7-Zip not found. Downloading standalone 7zr.exe from {url}")
    try:
        download(url, dest, "7zr.exe")
    except SystemExit:
        raise
    except Exception as e:
        die(
            "Could not download 7zr.exe automatically. "
            "Install 7-Zip from https://www.7-zip.org/ and re-run, or place 7zr.exe in the tools\\ folder. "
            f"Error: {e}"
        )
    if not dest.is_file() or dest.stat().st_size < 1000:
        die("Downloaded 7zr.exe looks invalid. Install 7-Zip from https://www.7-zip.org/ and re-run.")
    log(f"Using bundled extractor: {dest}")
    return str(dest)


def extract_7z_or_zip(archive: Path, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    if archive.suffix.lower() == ".zip":
        log(f"Extracting zip {archive.name}")
        with zipfile.ZipFile(archive, "r") as zf:
            zf.extractall(dest)
        return
    seven = ensure_7zr()
    log(f"Extracting with {seven}: {archive.name}")
    log("Large archive — this can take several minutes. 7-Zip progress will stream below.")
    # Stream output so the console is not silent for multi-GB extracts.
    # -bsp1 enables progress on stdout for modern 7-Zip.
    cmd = [seven, "x", str(archive), f"-o{dest}", "-y", "-bsp1"]
    r = subprocess.run(cmd)
    if r.returncode != 0:
        log("Retrying extract without progress switch...")
        r = subprocess.run([seven, "x", str(archive), f"-o{dest}", "-y"])
        if r.returncode != 0:
            die(f"7z extract failed (code {r.returncode})")
    log(f"Extraction finished into {dest}")


def find_portable_root() -> Path:
    """After extract, locate the folder that contains python_embeded and ComfyUI."""
    if (PORTABLE_DIR / "python_embeded").is_dir() and (PORTABLE_DIR / "ComfyUI").is_dir():
        return PORTABLE_DIR
    for child in PORTABLE_DIR.iterdir():
        if child.is_dir() and (child / "python_embeded").is_dir() and (child / "ComfyUI").is_dir():
            return child
    die(f"Could not locate portable layout under {PORTABLE_DIR}")


def ensure_portable(assets: dict) -> Path:
    if (PORTABLE_DIR / "python_embeded").is_dir() and (PORTABLE_DIR / "ComfyUI").is_dir():
        log("Portable runtime already present")
        return PORTABLE_DIR

    info = assets["portable_runtime"]
    archive = ROOT / info["name"]
    download(info["url"], archive, "ComfyUI portable NVIDIA")
    if PORTABLE_DIR.exists():
        shutil.rmtree(PORTABLE_DIR, ignore_errors=True)
    PORTABLE_DIR.mkdir(parents=True, exist_ok=True)
    extract_7z_or_zip(archive, PORTABLE_DIR)
    root = find_portable_root()
    if root != PORTABLE_DIR:
        log(f"Flattening nested portable root: {root}")
        for item in list(root.iterdir()):
            target = PORTABLE_DIR / item.name
            if target.exists():
                if target.is_dir():
                    shutil.rmtree(target)
                else:
                    target.unlink()
            shutil.move(str(item), str(target))
        try:
            root.rmdir()
        except OSError:
            pass
    return PORTABLE_DIR


def embed_python(root: Path) -> Path:
    py = root / "python_embeded" / "python.exe"
    if not py.is_file():
        die(f"Missing embedded Python: {py}")
    return py


def install_gguf(root: Path, py: Path) -> None:
    dest = root / "ComfyUI" / "custom_nodes" / "ComfyUI-GGUF"
    if dest.exists():
        shutil.rmtree(dest)
    if not GGUF_SRC.is_dir():
        die(f"Vendored ComfyUI-GGUF missing at {GGUF_SRC}")
    log(f"Copying ComfyUI-GGUF -> {dest}")
    shutil.copytree(GGUF_SRC, dest)
    req = dest / "requirements.txt"
    if req.is_file():
        log("Installing ComfyUI-GGUF requirements into portable Python")
        r = subprocess.run(
            [str(py), "-m", "pip", "install", "-r", str(req)],
            capture_output=True,
            text=True,
        )
        log(r.stdout[-2000:] if r.stdout else "")
        if r.returncode != 0:
            log(r.stderr or "")
            die("pip install of ComfyUI-GGUF requirements failed")


def install_models(root: Path, assets: dict) -> None:
    models_root = root / "ComfyUI" / "models"
    for m in assets["models"]:
        dest = models_root / m["directory"] / m["name"]
        download(m["url"], dest, m["name"])
        expected = m.get("sha256")
        if expected:
            actual = sha256_file(dest)
            if actual.lower() != expected.lower():
                die(f"SHA256 mismatch for {m['name']}: got {actual}, expected {expected}")
            log(f"SHA256 OK: {m['name']}")


def install_workflow(root: Path) -> Path:
    if not WORKFLOW_SRC.is_file():
        die(f"Missing workflow {WORKFLOW_SRC}")
    dest_dir = root / "ComfyUI" / "user" / "default" / "workflows"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / WORKFLOW_SRC.name
    shutil.copy2(WORKFLOW_SRC, dest)
    alt = root / "ComfyUI" / "workflows"
    alt.mkdir(parents=True, exist_ok=True)
    shutil.copy2(WORKFLOW_SRC, alt / WORKFLOW_SRC.name)
    log(f"Installed workflow -> {dest}")
    return dest


def start_comfy(root: Path, py: Path) -> subprocess.Popen:
    main_py = root / "ComfyUI" / "main.py"
    if not main_py.is_file():
        die(f"Missing {main_py}")
    log("Starting ComfyUI (NVIDIA)...")
    with COMFY_LOG.open("w", encoding="utf-8") as logf:
        proc = subprocess.Popen(
            [
                str(py),
                "-s",
                str(main_py),
                "--windows-standalone-build",
                "--listen",
                COMFY_HOST,
                "--port",
                str(COMFY_PORT),
            ],
            cwd=str(root / "ComfyUI"),
            stdout=logf,
            stderr=subprocess.STDOUT,
            creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0),
        )
    return proc


def wait_for_comfy(timeout: int = 180) -> None:
    url = f"http://{COMFY_HOST}:{COMFY_PORT}/system_stats"
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=5) as resp:
                if resp.status == 200:
                    log("ComfyUI is up")
                    return
        except Exception:
            pass
        time.sleep(2)
    die("Timed out waiting for ComfyUI to start. See Vidja_ComfyUI.log")


def smoke_test_workflow() -> dict:
    data = json.loads(WORKFLOW_SRC.read_text(encoding="utf-8"))
    for node in data.get("nodes", []):
        if node.get("type") == "EmptyHunyuanLatentVideo":
            node["widgets_values"] = [832, 480, 9, 1]
        if node.get("type") == "KSampler":
            wv = node.get("widgets_values") or [0, "randomize", 30, 6, "uni_pc", "simple", 1]
            wv[2] = 4
            node["widgets_values"] = wv
    return data


def queue_prompt(workflow: dict) -> str:
    prompt = {}
    if "nodes" in workflow:
        for node in workflow["nodes"]:
            nid = str(node["id"])
            inputs = {}
            wvals = list(node.get("widgets_values") or [])
            for inp in node.get("inputs") or []:
                link = inp.get("link")
                if link is not None:
                    inputs[inp["name"]] = ("LINK", link)
            t = node.get("type")
            if t in ("UnetLoaderGGUF", "CLIPLoaderGGUF", "VAELoader"):
                if wvals:
                    inputs["unet_name" if t == "UnetLoaderGGUF" else "clip_name" if t == "CLIPLoaderGGUF" else "vae_name"] = wvals[0]
                if t == "CLIPLoaderGGUF" and len(wvals) > 1:
                    inputs["type"] = wvals[1]
            elif t == "EmptyHunyuanLatentVideo":
                keys = ["width", "height", "length", "batch_size"]
                for i, k in enumerate(keys):
                    if i < len(wvals):
                        inputs[k] = wvals[i]
            elif t == "CLIPTextEncode":
                if wvals:
                    inputs["text"] = wvals[0]
            elif t == "KSampler":
                mapping = {"seed": 0, "steps": 2, "cfg": 3, "sampler_name": 4, "scheduler": 5, "denoise": 6}
                for k, idx in mapping.items():
                    if idx < len(wvals):
                        inputs[k] = wvals[idx]
            elif t == "ModelSamplingSD3":
                if wvals:
                    inputs["shift"] = wvals[0]
            elif t == "CreateVideo":
                if wvals:
                    inputs["fps"] = wvals[0]
            elif t == "SaveVideo":
                if wvals:
                    inputs["filename_prefix"] = wvals[0]
                    if len(wvals) > 1:
                        inputs["format"] = wvals[1]
                    if len(wvals) > 2:
                        inputs["codec"] = wvals[2]
            prompt[nid] = {"class_type": t, "inputs": inputs}

        link_src = {}
        for link in workflow.get("links") or []:
            if len(link) >= 5:
                link_src[link[0]] = (str(link[1]), link[2])

        for nid, entry in prompt.items():
            for k, v in list(entry["inputs"].items()):
                if isinstance(v, tuple) and v[0] == "LINK":
                    lid = v[1]
                    if lid in link_src:
                        entry["inputs"][k] = [link_src[lid][0], link_src[lid][1]]
                    else:
                        del entry["inputs"][k]
    else:
        prompt = workflow

    body = json.dumps({"prompt": prompt}).encode("utf-8")
    req = urllib.request.Request(
        f"http://{COMFY_HOST}:{COMFY_PORT}/prompt",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    pid = data.get("prompt_id") or data.get("promptId")
    if not pid:
        die(f"No prompt_id in response: {data}")
    log(f"Queued smoke-test prompt: {pid}")
    return pid


def wait_for_history(prompt_id: str, timeout: int = 900) -> dict:
    url = f"http://{COMFY_HOST}:{COMFY_PORT}/history/{prompt_id}"
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            if prompt_id in data and data[prompt_id].get("outputs"):
                log("Smoke test finished")
                return data[prompt_id]
            if prompt_id in data and data[prompt_id].get("status", {}).get("status_str") == "error":
                die(f"Prompt failed: {data[prompt_id]}")
        except Exception:
            pass
        time.sleep(3)
    die("Timed out waiting for smoke-test generation")


def find_video_outputs(root: Path) -> list:
    out_dir = root / "ComfyUI" / "output"
    videos = []
    if out_dir.is_dir():
        for p in out_dir.rglob("*"):
            if p.suffix.lower() in {".mp4", ".webm", ".mkv", ".avi", ".mov"} and p.stat().st_size > 0:
                videos.append(p)
    return videos


def package_ready(root: Path) -> None:
    if READY_ZIP.exists():
        READY_ZIP.unlink()
    log(f"Creating {READY_ZIP}")
    with zipfile.ZipFile(READY_ZIP, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=1) as zf:
        for path in root.rglob("*"):
            if path.is_file():
                if path.suffix.lower() in {".partial", ".log"} and path.name.startswith("Vidja_"):
                    continue
                arc = path.relative_to(root)
                zf.write(path, arcname=str(Path("ComfyUI_windows_portable") / arc))
    log(f"Created {READY_ZIP} ({READY_ZIP.stat().st_size // (1024*1024)} MB)")


def open_browser() -> None:
    url = f"http://{COMFY_HOST}:{COMFY_PORT}"
    try:
        if sys.platform == "win32":
            os.startfile(url)  # type: ignore[attr-defined]
        else:
            subprocess.Popen(["xdg-open", url])
    except Exception as e:
        log(f"Could not open browser: {e}")


def main() -> int:
    LOG.write_text("", encoding="utf-8")
    log("Vidja setup starting")
    assets = load_assets()

    root = ensure_portable(assets)
    py = embed_python(root)
    install_gguf(root, py)
    install_models(root, assets)
    install_workflow(root)

    proc = start_comfy(root, py)
    try:
        wait_for_comfy()
        wf = smoke_test_workflow()
        pid = queue_prompt(wf)
        wait_for_history(pid)
        videos = find_video_outputs(root)
        if not videos:
            die("Smoke test completed but no video file was found under ComfyUI/output")
        log(f"Verified video output: {videos[0]} ({videos[0].stat().st_size} bytes)")
        package_ready(root)
        open_browser()
        log("Setup complete. ComfyUI is still running. Close the window or Ctrl+C to stop.")
        try:
            proc.wait()
        except KeyboardInterrupt:
            log("Interrupted by user")
            proc.terminate()
    except SystemExit:
        proc.terminate()
        raise
    except Exception as e:
        proc.terminate()
        die(str(e))
    return 0


if __name__ == "__main__":
    sys.exit(main())
