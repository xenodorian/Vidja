import os, sys, json, time, uuid, shutil, hashlib, subprocess, urllib.request, urllib.parse, webbrowser, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LOG = ROOT / "Vidja_Setup.log"
PORTABLE = ROOT / "Vidja_Portable"
ARCHIVE = ROOT / "_downloads" / "ComfyUI_windows_portable_nvidia.7z"
SEVENZIP = ROOT / "_downloads" / "7zr.exe"
SERVER_LOG = ROOT / "Vidja_ComfyUI.log"

COMFY_URL = "https://github.com/Comfy-Org/ComfyUI/releases/latest/download/ComfyUI_windows_portable_nvidia.7z"
SEVENZIP_URL = "https://www.7-zip.org/a/7zr.exe"
GGUF_REPO = "https://github.com/city96/ComfyUI-GGUF/archive/refs/heads/main.zip"
MODELS = [
    ("Wan2.1-T2V-1.3B-Q4_K_S.gguf",
     "https://huggingface.co/samuelchristlie/Wan2.1-T2V-1.3B-GGUF/resolve/main/Wan2.1-T2V-1.3B-Q4_K_S.gguf?download=true",
     "unet", "9fa296a9ee5433750cd59cc451c169af735c9d7c0c4459c5e645da6903cc15fa"),
    ("umt5-xxl-encoder-Q3_K_S.gguf",
     "https://huggingface.co/city96/umt5-xxl-encoder-gguf/resolve/main/umt5-xxl-encoder-Q3_K_S.gguf?download=true",
     "clip", "f64f8d6dc4d8a24276df69d0ccea789aae686f7417950a41e6568c30cb478a5c"),
    ("wan_2.1_vae.safetensors",
     "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/vae/wan_2.1_vae.safetensors?download=true",
     "vae", "2fc39d31359a4b0a64f55876d8ff7fa8d780956ae2cb13463b0223e15148976b")
]

def log(msg):
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as f: f.write(line + "\n")

def run(cmd, cwd=None, check=True):
    log("RUN: " + " ".join(map(str, cmd)))
    p = subprocess.run(cmd, cwd=cwd, text=True)
    if check and p.returncode:
        raise RuntimeError(f"Command failed with exit code {p.returncode}: {' '.join(map(str, cmd))}")
    return p.returncode

def download(url, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        log(f"Using existing download: {dest.name}")
        return
    log(f"Downloading: {url}")
    run(["curl.exe","-L","--fail","--retry","8","--retry-delay","3","--continue-at","-",url,"-o",str(dest)])

def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(8*1024*1024), b""): h.update(b)
    return h.hexdigest()

def wait_http(url, timeout=120):
    end=time.time()+timeout
    while time.time()<end:
        try:
            urllib.request.urlopen(url, timeout=5).read(32)
            return True
        except Exception:
            time.sleep(2)
    return False

def api_post(url, obj):
    data=json.dumps(obj).encode()
    req=urllib.request.Request(url, data=data, headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req, timeout=30) as r: return json.loads(r.read())

def build_test_prompt():
    # ComfyUI API-format graph. The final test deliberately uses 9 frames and 4 steps
    # so setup verifies model loading and GPU execution without committing to a long run.
    return {
      "38":{"class_type":"CLIPLoaderGGUF","inputs":{"clip_name":"umt5-xxl-encoder-Q3_K_S.gguf","type":"wan"}},
      "39":{"class_type":"VAELoader","inputs":{"vae_name":"wan_2.1_vae.safetensors"}},
      "37":{"class_type":"UnetLoaderGGUF","inputs":{"unet_name":"Wan2.1-T2V-1.3B-Q4_K_S.gguf"}},
      "40":{"class_type":"EmptyHunyuanLatentVideo","inputs":{"width":832,"height":480,"length":9,"batch_size":1}},
      "6":{"class_type":"CLIPTextEncode","inputs":{"clip":["38",0],"text":"a fox moving quickly in a beautiful winter landscape, tracking camera"}},
      "7":{"class_type":"CLIPTextEncode","inputs":{"clip":["38",0],"text":"static, blurry, low quality, distorted, extra limbs, text, watermark"}},
      "48":{"class_type":"ModelSamplingSD3","inputs":{"model":["37",0],"shift":8}},
      "3":{"class_type":"KSampler","inputs":{"seed":82628696717253,"steps":4,"cfg":6,"sampler_name":"uni_pc","scheduler":"simple","denoise":1,"model":["48",0],"positive":["6",0],"negative":["7",0],"latent_image":["40",0]}},
      "8":{"class_type":"VAEDecode","inputs":{"samples":["3",0],"vae":["39",0]}},
      "49":{"class_type":"CreateVideo","inputs":{"images":["8",0],"fps":16,"bit_depth":"auto","color_space":"sRGB","codec":"none"}},
      "50":{"class_type":"SaveVideo","inputs":{"video":["49",0],"filename_prefix":"video/Vidja_AutoTest","format":{"format":"mp4","codec":"h264","encoding":{"encoding":"re-encode","crf":23}}}}
    }

def wait_generation(prompt_id, timeout=3600):
    end=time.time()+timeout
    while time.time()<end:
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:8188/history/{prompt_id}",timeout=10) as r:
                h=json.loads(r.read())
            if prompt_id in h:
                entry=h[prompt_id]
                status=entry.get("status",{})
                if status.get("status_str") == "success":
                    return entry
                if status.get("status_str") == "error":
                    raise RuntimeError(json.dumps(status, ensure_ascii=False))
        except urllib.error.HTTPError:
            pass
        except urllib.error.URLError:
            pass
        time.sleep(3)
    raise TimeoutError("ComfyUI generation timed out")

def package_runtime():
    out_zip = ROOT / "Vidja_ComfyUI_Ready.zip"
    if out_zip.exists():
        out_zip.unlink()
    test_output = PORTABLE / "ComfyUI" / "output"
    if test_output.exists():
        # The smoke-test video proves generation worked but is not required in the
        # distributable runtime.
        shutil.rmtree(test_output)
    log("Packaging the complete tested runtime. This may take several minutes.")
    count = 0
    with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_STORED, allowZip64=True) as z:
        for p in PORTABLE.rglob("*"):
            if p.is_file():
                rel = p.relative_to(PORTABLE)
                z.write(p, rel.as_posix())
                count += 1
                if count % 5000 == 0:
                    log(f"Packaged {count} files...")
    log(f"Final package created: {out_zip} ({out_zip.stat().st_size} bytes)")
    return out_zip

def main():
    LOG.write_text("", encoding="utf-8")
    log("Starting fully automatic Vidja setup.")
    if sys.version_info < (3,10):
        raise RuntimeError("Vidja setup requires system Python 3.10 or newer.")

    downloads=ROOT/"_downloads"
    downloads.mkdir(exist_ok=True)

    # 1. Obtain and extract the official NVIDIA portable runtime.
    if not (PORTABLE/"ComfyUI"/"main.py").exists():
        download(COMFY_URL, ARCHIVE)
        download(SEVENZIP_URL, SEVENZIP)
        if PORTABLE.exists(): shutil.rmtree(PORTABLE)
        PORTABLE.mkdir()
        run([str(SEVENZIP),"x",str(ARCHIVE),f"-o{PORTABLE}","-y"])
        # The archive normally contains ComfyUI_windows_portable at its root.
        nested=PORTABLE/"ComfyUI_windows_portable"
        if nested.exists():
            tmp=ROOT/"Vidja_Portable_tmp"
            if tmp.exists(): shutil.rmtree(tmp)
            nested.rename(tmp)
            shutil.rmtree(PORTABLE)
            tmp.rename(PORTABLE)
    else:
        log("Existing Vidja_Portable runtime detected.")

    comfy=PORTABLE/"ComfyUI"
    pyexe=PORTABLE/"python_embeded"/"python.exe"
    if not comfy.exists() or not pyexe.exists():
        raise RuntimeError("Portable ComfyUI extraction is incomplete.")

    # 2. Install the vendored GGUF node directly from the repository snapshot.
    node_src=ROOT/"custom_nodes"/"ComfyUI-GGUF"
    node_dst=comfy/"custom_nodes"/"ComfyUI-GGUF"
    if node_src.exists():
        if node_dst.exists(): shutil.rmtree(node_dst)
        shutil.copytree(node_src,node_dst,ignore=shutil.ignore_patterns(".git","__pycache__"))
    else:
        log("Vendored GGUF node missing; downloading upstream node.")
        tmp=downloads/"ComfyUI-GGUF"
        if tmp.exists(): shutil.rmtree(tmp)
        download(GGUF_REPO,downloads/"gguf.zip")
        with zipfile.ZipFile(downloads/"gguf.zip") as z: z.extractall(downloads/"gguf_extract")
        extracted=next((p for p in (downloads/"gguf_extract").iterdir() if p.is_dir()),None)
        if not extracted: raise RuntimeError("Could not extract ComfyUI-GGUF.")
        shutil.copytree(extracted,node_dst,ignore=shutil.ignore_patterns(".git","__pycache__"))
    run([str(pyexe),"-s","-m","pip","install","-r",str(node_dst/"requirements.txt")])

    # 3. Install the exact model files and verify their SHA256 hashes.
    for name,url,folder,expected in MODELS:
        dest=comfy/"models"/folder/name
        download(url,dest)
        actual=sha256(dest)
        log(f"SHA256 {name}: {actual}")
        if actual.lower()!=expected.lower():
            raise RuntimeError(f"SHA256 mismatch for {name}: expected {expected}, got {actual}")

    # 4. Copy the human-editable workflow into the runtime.
    wf=ROOT/"workflows"/"wan2.1_t2v_1.3b_gguf_3060.json"
    if wf.exists():
        (comfy/"workflows").mkdir(exist_ok=True)
        shutil.copy2(wf,comfy/"workflows"/wf.name)

    # 5. Start ComfyUI and wait for its HTTP API.
    log("Starting ComfyUI.")
    server_out=SERVER_LOG.open("w",encoding="utf-8")
    proc=subprocess.Popen([str(pyexe),"-s","ComfyUI/main.py","--windows-standalone-build"],cwd=str(PORTABLE),stdout=server_out,stderr=subprocess.STDOUT,creationflags=getattr(subprocess,"CREATE_NEW_PROCESS_GROUP",0))
    if not wait_http("http://127.0.0.1:8188/system_stats",180):
        server_out.close()
        raise RuntimeError("ComfyUI did not start. Inspect Vidja_ComfyUI.log.")
    log("ComfyUI API is online.")

    # 6. Automatically execute a real GPU smoke test.
    prompt=build_test_prompt()
    result=api_post("http://127.0.0.1:8188/prompt",{"prompt":prompt,"client_id":str(uuid.uuid4())})
    if "prompt_id" not in result:
        raise RuntimeError("ComfyUI rejected the automatic test prompt: "+json.dumps(result))
    prompt_id=result["prompt_id"]
    log("Automatic generation queued: "+prompt_id)
    history=wait_generation(prompt_id)
    log("Automatic generation completed successfully.")

    # 7. Confirm a video output exists.
    outputs=history.get("outputs",{})
    videos=[]
    for node in outputs.values():
        videos.extend(node.get("videos",[]))
    if not videos:
        # Some versions expose video outputs differently. The output directory is authoritative.
        videos=list((comfy/"output"/"video").rglob("*")) if (comfy/"output"/"video").exists() else []
    videos=[p for p in videos if isinstance(p,Path) and p.is_file()] if videos else []
    if not videos:
        raise RuntimeError("Generation reported success but no video file was found.")
    log("Verified generated video: "+str(videos[0]))

    # 8. Automatically build the final self-contained ZIP after the smoke test.
    final_zip = package_runtime()

    # 9. Open the UI. Leave the server running for immediate use.
    webbrowser.open("http://127.0.0.1:8188")
    log("Vidja is ready. ComfyUI remains running.")
    print("\nVIDJA SETUP COMPLETE")
    print("A real automatic Wan GPU smoke test succeeded.")
    print("Generated test video: "+str(videos[0]))
    print("Final package: "+str(final_zip))
    print("ComfyUI: http://127.0.0.1:8188")

if __name__=="__main__":
    try:
        main()
    except Exception as e:
        log("FATAL: "+repr(e))
        print("\nSETUP FAILED: "+str(e))
        sys.exit(1)
