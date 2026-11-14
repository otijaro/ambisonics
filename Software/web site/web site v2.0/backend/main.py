import os
import uuid
import json
import logging
import shutil
import time
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone, timedelta

from backend.services.cleanup import cleanup_expired_files

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.routers.auth import router as auth_router
from backend.routers.processing_requests import router as pr_router
from backend.processor import convert_audio as native_convert_audio
from backend.demo_processor import process_demo as native_process_demo
from backend.core_dsp import load_sofa
from backend.database import get_db
from backend import models, schemas
from backend.dependencies import get_optional_user

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ambisonic-backend")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "backend", "static")
CODIGOS_DIR = os.path.join(BASE_DIR, "Codigos")
FEEDBACK_FILE = os.path.join(BASE_DIR, "backend", "feedback.json")
HRTF_PATH = os.path.join(CODIGOS_DIR, "hrtf.sofa")

os.makedirs(STATIC_DIR, exist_ok=True)

# Global variables to cache HRTF data
app_state = {
    "hrtf": None,
    "pos": None
}

async def periodic_cleanup():
    logger.info("Ejecutando limpieza inicial de archivos expirados al inicio del servidor...")
    try:
        # Se ejecuta en un hilo separado para no bloquear el event loop (I/O bloqueante)
        await asyncio.to_thread(cleanup_expired_files)
    except Exception as e:
        logger.error(f"Error en limpieza inicial: {e}")

    while True:
        try:
            # Esperar 24 horas (24 * 60 * 60 segundos)
            await asyncio.sleep(86400)
            logger.info("Ejecutando limpieza periódica (24h)...")
            await asyncio.to_thread(cleanup_expired_files)
        except asyncio.CancelledError:
            logger.info("Tarea de limpieza periódica cancelada.")
            break
        except Exception as e:
            logger.error(f"Error en limpieza periódica: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    logger.info("Cargando archivo HRTF/SOFA en memoria RAM (una sola vez)...")
    if os.path.exists(HRTF_PATH):
        try:
            hrtf, pos = load_sofa(HRTF_PATH)
            app_state["hrtf"] = hrtf
            app_state["pos"] = pos
            logger.info("HRTF cargado exitosamente.")
        except Exception as e:
            logger.error(f"Error al cargar HRTF: {e}")
    else:
        logger.warning(f"Archivo HRTF no encontrado en {HRTF_PATH}. El procesamiento 3D usará fallback.")
    
    # Iniciar la tarea de limpieza en segundo plano
    cleanup_task = asyncio.create_task(periodic_cleanup())
    
    yield
    
    # Shutdown logic
    logger.info("Apagando servidor...")
    cleanup_task.cancel()
    app_state["hrtf"] = None
    app_state["pos"] = None

app = FastAPI(title="Ambisonic Backend", lifespan=lifespan)

origins_env = os.getenv("FRONTEND_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000,https://ambisonic.vercel.app")
frontend_origins = [orig.strip() for orig in origins_env.split(",") if orig.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=frontend_origins,
    allow_origin_regex=r"^http://(10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+|172\.(1[6-9]|2[0-9]|3[0-1])\.\d+\.\d+):3000$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(pr_router)

# Mount static folder to serve generated audio files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}

@app.post("/api/convert")
async def convert_audio(
    audio: UploadFile = File(...),
    mode: str = Form("auto"),
    db: Session = Depends(get_db),
    user: models.User | None = Depends(get_optional_user)
):
    session_id = str(uuid.uuid4())
    session_dir = os.path.join(STATIC_DIR, session_id)
    os.makedirs(session_dir, exist_ok=True)

    # 1. Registrar ProcessingRequest inicial
    valid_mode = mode if mode in ["stereo", "tetra_4mic"] else "stereo"
    db_req = models.ProcessingRequest(
        original_filename=audio.filename or "unknown.wav",
        input_mode=valid_mode,
        status="processing",
        user_id=user.id if user else None,
        requested_at=datetime.now(timezone.utc)
    )
    db.add(db_req)
    db.commit()
    db.refresh(db_req)

    # Save incoming audio file
    file_ext = os.path.splitext(audio.filename)[1]
    if not file_ext:
        file_ext = ".wav"  # fallback
    input_path = os.path.join(session_dir, f"input{file_ext}")

    logger.info(f"Guardando input audio en {input_path}")
    with open(input_path, "wb") as f:
        shutil.copyfileobj(audio.file, f)

    # Ejecutar procesamiento nativo real
    logger.info(f"Ejecutando procesamiento nativo de conversión con modo {mode}")
    try:
        original_duration, proc_time, sr = native_convert_audio(
            input_path=input_path,
            output_dir=session_dir,
            mode=mode,
            hrtf=app_state["hrtf"],
            pos=app_state["pos"]
        )
        db_req.status = "completed"
        db_req.processing_seconds = proc_time
        db_req.original_duration_seconds = original_duration
        db_req.processing_sample_rate_hz = sr
        if original_duration > 0:
            db_req.processing_percentage = (proc_time / original_duration) * 100
        else:
            db_req.processing_percentage = 0.0
        db_req.finished_at = datetime.now(timezone.utc)
        db.commit()
    except Exception as e:
        logger.error(f"Error executing native convert: {str(e)}")
        db_req.status = "failed"
        db_req.error_message = str(e)
        db_req.finished_at = datetime.now(timezone.utc)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error durante el procesamiento del audio: {str(e)}"
        )

    # Expected output files
    outputs = [
        {
            "key": "binaural",
            "wavUrl": f"/static/{session_id}/output_binaural.wav",
            "mp3Url": f"/static/{session_id}/output_binaural.mp3"
        },
        {
            "key": "binaural_3d",
            "wavUrl": f"/static/{session_id}/output_binaural_3D_perceptual.wav",
            "mp3Url": f"/static/{session_id}/output_binaural_3D_perceptual.mp3"
        }
    ]

    # Registrar Archivos Físicos Reales
    now = datetime.now(timezone.utc)
    expires = now + timedelta(hours=24)

    if os.path.exists(input_path):
        db.add(models.TemporaryFile(
            processing_request_id=db_req.id,
            file_type="input",
            storage_path=input_path,
            expires_at=expires,
            created_at=now
        ))

    # Verify that files were created
    available_outputs = []
    for output in outputs:
        # Check wav exists
        wav_filename = os.path.basename(output["wavUrl"])
        wav_path = os.path.join(session_dir, wav_filename)
        if os.path.exists(wav_path):
            db.add(models.TemporaryFile(
                processing_request_id=db_req.id,
                file_type=output["key"],
                storage_path=wav_path,
                expires_at=expires,
                created_at=now
            ))
            
            out_item = {"key": output["key"], "wavUrl": output["wavUrl"]}
            if "mp3Url" in output:
                # El MP3 se genera asíncronamente, por lo que asumimos que existirá
                out_item["mp3Url"] = output["mp3Url"]
            available_outputs.append(out_item)

    db.commit()

    logger.info(f"Conversion completa. Archivos disponibles: {len(available_outputs)}.")
    return {
        "outputs": available_outputs,
        "processing_seconds": proc_time,
        "original_duration_seconds": original_duration
    }

@app.post("/api/demo")
async def run_demo_notebook(
    audio: UploadFile = File(...),
    direccion: str = Form(default="0"),
    altura: str = Form(default="0"),
    apertura: str = Form(default="0"),
    movimiento: str = Form(default="0"),
    original_mode: bool = Form(default=True)
):
    # --- VALIDACIÓN DE PARÁMETROS ---
    def parse_and_clamp(val_str: str, v_min: float, v_max: float, default: float) -> float:
        try:
            val = float(val_str)
            if np.isnan(val) or not np.isfinite(val):
                return default
            return max(v_min, min(v_max, val))
        except (ValueError, TypeError):
            return default

    import numpy as np # Necesario para validación (lo importamos aquí o asumimos que lo ponemos arriba)
    
    dir_val = parse_and_clamp(direccion, -90.0, 90.0, 0.0)
    alt_val = parse_and_clamp(altura, 0.0, 100.0, 0.0)
    ape_val = parse_and_clamp(apertura, 0.0, 100.0, 0.0)
    mov_val = parse_and_clamp(movimiento, 0.0, 100.0, 0.0)
    # --------------------------------

    session_id = str(uuid.uuid4())
    session_dir = os.path.join(STATIC_DIR, session_id)
    os.makedirs(session_dir, exist_ok=True)
    
    # Save audio input
    file_ext = os.path.splitext(audio.filename)[1] if audio.filename else ".wav"
    if not file_ext:
        file_ext = ".wav"
    input_path = os.path.join(session_dir, f"input{file_ext}")

    logger.info(f"Guardando input audio en {input_path}")
    with open(input_path, "wb") as f:
        shutil.copyfileobj(audio.file, f)

    logger.info(f"Ejecutando procesamiento nativo de demo con params: dir={dir_val}, alt={alt_val}, ap={ape_val}, mov={mov_val}")
    try:
        native_process_demo(
            input_path=input_path,
            output_dir=session_dir,
            direccion=dir_val,
            altura=alt_val,
            apertura=ape_val,
            movimiento=mov_val,
            hrtf=app_state["hrtf"],
            pos=app_state["pos"],
            original_mode=original_mode
        )
    except Exception as e:
        logger.error(f"Error executing native demo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error durante el procesamiento del demo: {str(e)}"
        )

    # Check for expected output preview files
    binaural_wav = f"/static/{session_id}/preview_binaural.wav"
    binaural_mp3 = f"/static/{session_id}/preview_binaural.mp3"
    perceptual_wav = f"/static/{session_id}/preview_3d_perceptual.wav"
    perceptual_mp3 = f"/static/{session_id}/preview_3d_perceptual.mp3"

    res = {
        "binaural": {},
        "binaural_3d": {}
    }

    if os.path.exists(os.path.join(session_dir, "preview_binaural.wav")):
        res["binaural"]["wavUrl"] = binaural_wav
        res["binaural"]["mp3Url"] = binaural_mp3 # Asíncrono
    if os.path.exists(os.path.join(session_dir, "preview_3d_perceptual.wav")):
        res["binaural_3d"]["wavUrl"] = perceptual_wav
        res["binaural_3d"]["mp3Url"] = perceptual_mp3 # Asíncrono

    logger.info("Demo execution complete.")
    return res

class FeedbackPayload(BaseModel):
    nombre: str
    correo: str
    mensaje: str

@app.post("/api/feedback")
async def save_feedback(payload: FeedbackPayload, db: Session = Depends(get_db)):
    try:
        has_pii = bool(payload.nombre or payload.correo)
        db_sugg = models.Suggestion(
            name=payload.nombre if payload.nombre else None,
            email=payload.correo if payload.correo else None,
            message=payload.mensaje,
            consent_given=True if has_pii else False,
            created_at=datetime.now(timezone.utc)
        )
        db.add(db_sugg)
        db.commit()
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error saving feedback: {str(e)}")
        raise HTTPException(status_code=500, detail="No se pudo guardar la sugerencia.")
