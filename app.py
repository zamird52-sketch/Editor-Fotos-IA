import os
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)
MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_MB", "100")) * 1024 * 1024
ALLOWED_EXTENSIONS = {".mp3", ".wav", ".flac", ".m4a", ".ogg", ".aac", ".wma", ".mp4"}

app = FastAPI(title="Separan Voces", version="1.0.0")
app.mount("/outputs", StaticFiles(directory=str(OUTPUT_DIR)), name="outputs")


@app.get("/", response_class=HTMLResponse)
def home():
    return (BASE_DIR / "index.html").read_text(encoding="utf-8")


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "Separan Voces"}


@app.post("/api/separate")
async def separate_audio(file: UploadFile = File(...)):
    original_name = Path(file.filename or "audio.wav").name
    extension = Path(original_name).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=415, detail="Formato no compatible. Probá MP3, WAV, FLAC, M4A u OGG.")

    job_id = uuid.uuid4().hex
    job_dir = OUTPUT_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=False)
    input_path = job_dir / f"input{extension}"
    demucs_out = job_dir / "demucs"
    try:
        total = 0
        with input_path.open("wb") as destination:
            while chunk := await file.read(1024 * 1024):
                total += len(chunk)
                if total > MAX_UPLOAD_BYTES:
                    raise HTTPException(status_code=413, detail=f"El archivo supera el límite de {MAX_UPLOAD_BYTES // (1024 * 1024)} MB.")
                destination.write(chunk)
        if total == 0:
            raise HTTPException(status_code=400, detail="El archivo está vacío.")

        command = [
            "python", "-m", "demucs", "--two-stems", "vocals",
            "-n", os.getenv("DEMUCS_MODEL", "htdemucs"),
            "-o", str(demucs_out), str(input_path)
        ]
        try:
            process = subprocess.run(command, capture_output=True, text=True, timeout=int(os.getenv("PROCESS_TIMEOUT_SECONDS", "1800")))
        except subprocess.TimeoutExpired:
            raise HTTPException(status_code=504, detail="El procesamiento tardó demasiado. Probá con un archivo más corto.")
        if process.returncode != 0:
            detail = (process.stderr or process.stdout or "Falló el modelo de separación.")[-1200:]
            raise HTTPException(status_code=500, detail="No se pudo separar el audio. " + detail)

        stem_dir = demucs_out / os.getenv("DEMUCS_MODEL", "htdemucs") / input_path.stem
        vocals_source = stem_dir / "vocals.wav"
        instrumental_source = stem_dir / "no_vocals.wav"
        if not vocals_source.exists() or not instrumental_source.exists():
            raise HTTPException(status_code=500, detail="El modelo terminó pero no se encontraron las dos pistas de salida.")
        vocals_dest = job_dir / "voz-aislada.wav"
        instrumental_dest = job_dir / "instrumental.wav"
        shutil.copy2(vocals_source, vocals_dest)
        shutil.copy2(instrumental_source, instrumental_dest)
        shutil.rmtree(demucs_out, ignore_errors=True)
        input_path.unlink(missing_ok=True)
        return {
            "job_id": job_id,
            "vocals_url": f"/outputs/{job_id}/voz-aislada.wav",
            "instrumental_url": f"/outputs/{job_id}/instrumental.wav",
            "vocals_filename": "voz-aislada.wav",
            "instrumental_filename": "instrumental.wav"
        }
    except HTTPException:
        shutil.rmtree(job_dir, ignore_errors=True)
        raise
    except Exception as exc:
        shutil.rmtree(job_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=f"Error procesando el audio: {exc}") from exc
    finally:
        await file.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
