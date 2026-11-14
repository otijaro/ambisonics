import os
import uuid
import json
import logging
import shutil
import time
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone, timedelta

import soundfile as sf
from backend.services.cleanup import cleanup_expired_files

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status, Depends
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.routers.auth import router as auth_router
from backend.routers.processing_requests import router as pr_router
from backend.processor import convert_audio as native_convert_audio
from backend.demo_processor import process_demo as native_process_demo
from backend.core_dsp import (
    load_sofa,
    validate_sample_rate,
    get_sadie_sofa_path,
    SUPPORTED_SAMPLING_RATES,
    SOFA_FILENAMES
)
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

# Cache de archivos SOFA/HRTF por frecuencia de muestreo
app_state = {
    "sofa_cache": {},   # sr -> (hrtf, pos)
    "hrtf": None,       # Compatibilidad con accesos directos
    "pos": None
}

def get_sofa_for_sr(sr: int):
    """Obtiene la tupla (hrtf, pos) correspondiente a la frecuencia de muestreo sr."""
    validate_sample_rate(sr)
    if sr in app_state["sofa_cache"]:
        return app_state["sofa_cache"][sr]
    try:
        path = get_sadie_sofa_path(sr, BASE_DIR)
        logger.info(f"Cargando bajo demanda SOFA SADIE II D1 para {sr} Hz desde {path}...")
        ir, pos = load_sofa(path)
        app_state["sofa_cache"][sr] = (ir, pos)
        return ir, pos
    except Exception as e:
        logger.error(f"Error al cargar SOFA para {sr} Hz: {e}")
        return None, None

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
    # Startup logic: verificación de tablas en base de datos
    try:
        from backend.database import engine, Base
        from backend import models
        Base.metadata.create_all(bind=engine)
        logger.info("Base de datos: tablas verificadas/creadas exitosamente.")
    except Exception as e:
        logger.warning(f"No se pudieron verificar/crear tablas en base de datos: {e}")

    logger.info("Cargando bases SOFA SADIE II D1 en memoria RAM para 44.1, 48 y 96 kHz...")
    for sr_target in SUPPORTED_SAMPLING_RATES:
        try:
            sofa_file = get_sadie_sofa_path(sr_target, BASE_DIR)
            logger.info(f"Cargando SOFA {sr_target} Hz desde {sofa_file}...")
            ir, pos = load_sofa(sofa_file)
            app_state["sofa_cache"][sr_target] = (ir, pos)
            logger.info(f"SOFA SADIE II D1 para {sr_target} Hz cargado exitosamente (M={pos.shape[0]}, Taps={ir.shape[2]}).")
        except Exception as e:
            logger.error(f"Error cargando SOFA para {sr_target} Hz: {e}")

    # Asignar referencia predeterminada a 44.1 kHz para retrocompatibilidad
    if 44100 in app_state["sofa_cache"]:
        app_state["hrtf"] = app_state["sofa_cache"][44100][0]
        app_state["pos"] = app_state["sofa_cache"][44100][1]
    
    # Iniciar la tarea de limpieza en segundo plano
    cleanup_task = asyncio.create_task(periodic_cleanup())
    
    yield
    
    # Shutdown logic
    logger.info("Apagando servidor...")
    cleanup_task.cancel()
    app_state["sofa_cache"].clear()
    app_state["hrtf"] = None
    app_state["pos"] = None

app = FastAPI(title="Ambisonic Backend", lifespan=lifespan)

MAX_CONCURRENT_DSP = int(os.getenv("MAX_CONCURRENT_DSP", "2"))
dsp_semaphore = asyncio.Semaphore(MAX_CONCURRENT_DSP)

origins_env = os.getenv("FRONTEND_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000,https://ambisonic.vercel.app")
frontend_origins = [orig.strip() for orig in origins_env.split(",") if orig.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=frontend_origins,
    allow_origin_regex=r"^http://(10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+|172\.(1[6-9]|2[0-9]|3[0-1])\.\d+\.\d+)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(auth_router)
app.include_router(pr_router)

# Mount static folder to serve generated audio files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/api/download/{session_id}/{filename}")
async def download_session_file(session_id: str, filename: str):
    """Descarga forzada (Content-Disposition: attachment) de archivos generados en una sesión.
    
    Garantiza que el navegador descargue el archivo directamente sin reproducirlo ni abrirlo
    en una pestaña del navegador, tanto en desarrollo local como entre orígenes cruzados (CORS).
    """
    allowed_filenames = {
        "output_binaural.wav",
        "output_binaural.mp3",
        "output_binaural_3D_perceptual.wav",
        "output_binaural_3D_perceptual.mp3",
        "output_foa.wav",
    }
    if filename not in allowed_filenames:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nombre de archivo no permitido para descarga directa."
        )

    session_dir = os.path.abspath(os.path.join(STATIC_DIR, session_id))
    if not session_dir.startswith(os.path.abspath(STATIC_DIR)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado."
        )

    file_path = os.path.abspath(os.path.join(session_dir, filename))
    if not file_path.startswith(session_dir) or not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El archivo {filename} no existe o ya ha expirado."
        )

    media_type = "audio/mpeg" if filename.endswith(".mp3") else "audio/wav"
    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=filename,
    )

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

    # Save incoming audio file
    file_ext = os.path.splitext(audio.filename)[1].lower() if audio.filename else ".wav"
    if not file_ext or file_ext not in [".wav", ".mp3"]:
        shutil.rmtree(session_dir, ignore_errors=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato no soportado ({file_ext}). Solo se admiten archivos WAV o MP3."
        )
    input_path = os.path.join(session_dir, f"input{file_ext}")

    logger.info(f"Guardando input audio en {input_path}")
    with open(input_path, "wb") as f:
        shutil.copyfileobj(audio.file, f)

    # Validar formato y frecuencia de muestreo admitida (44.1, 48 o 96 kHz sin remuestreo)
    try:
        info = sf.info(input_path)
        input_sr = info.samplerate
    except Exception as e:
        logger.warning(f"Error al leer audio en convert: {e}")
        shutil.rmtree(session_dir, ignore_errors=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo procesar el archivo de audio. Verifica que sea un WAV o MP3 válido."
        )

    try:
        validated_sr = validate_sample_rate(input_sr)
    except ValueError as ve:
        logger.warning(f"Audio rechazado por frecuencia de muestreo no admitida: {ve}")
        shutil.rmtree(session_dir, ignore_errors=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )

    # 1. Registrar ProcessingRequest inicial
    valid_mode = mode if mode in ["stereo", "tetra_4mic"] else "stereo"
    db_req = models.ProcessingRequest(
        original_filename=audio.filename or "unknown.wav",
        input_mode=valid_mode,
        status="processing",
        input_sample_rate_hz=input_sr,
        user_id=user.id if user else None,
        requested_at=datetime.now(timezone.utc)
    )
    db.add(db_req)
    db.commit()
    db.refresh(db_req)

    # Obtener SOFA SADIE II D1 correspondiente a la frecuencia nativa
    hrtf_sr, pos_sr = get_sofa_for_sr(validated_sr)

    # Ejecutar procesamiento nativo real en worker thread para no bloquear el event loop
    logger.info(f"Ejecutando procesamiento nativo de conversión en worker thread con modo {mode} (sr={validated_sr} Hz)")
    try:
        async with dsp_semaphore:
            original_duration, proc_time, sr = await asyncio.to_thread(
                native_convert_audio,
                input_path=input_path,
                output_dir=session_dir,
                mode=mode,
                hrtf=hrtf_sr,
                pos=pos_sr
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
    except ValueError as ve:
        logger.warning(f"Validación fallida en conversión: {ve}")
        db_req.status = "failed"
        db_req.error_message = str(ve)
        db_req.finished_at = datetime.now(timezone.utc)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
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
            "mp3Url": f"/static/{session_id}/output_binaural.mp3",
            "downloadWavUrl": f"/api/download/{session_id}/output_binaural.wav",
            "downloadMp3Url": f"/api/download/{session_id}/output_binaural.mp3",
        },
        {
            "key": "binaural_3d",
            "wavUrl": f"/static/{session_id}/output_binaural_3D_perceptual.wav",
            "mp3Url": f"/static/{session_id}/output_binaural_3D_perceptual.mp3",
            "downloadWavUrl": f"/api/download/{session_id}/output_binaural_3D_perceptual.wav",
            "downloadMp3Url": f"/api/download/{session_id}/output_binaural_3D_perceptual.mp3",
        },
        {
            "key": "foa",
            "wavUrl": f"/api/download/{session_id}/output_foa.wav",
            "downloadUrl": f"/api/download/{session_id}/output_foa.wav",
            "downloadWavUrl": f"/api/download/{session_id}/output_foa.wav",
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
            if "downloadWavUrl" in output:
                out_item["downloadWavUrl"] = output["downloadWavUrl"]
            if "downloadMp3Url" in output:
                out_item["downloadMp3Url"] = output["downloadMp3Url"]
            if "downloadUrl" in output:
                out_item["downloadUrl"] = output["downloadUrl"]
            if "mp3Url" in output:
                mp3_filename = os.path.basename(output["mp3Url"])
                mp3_path = os.path.join(session_dir, mp3_filename)
                if os.path.exists(mp3_path) and os.path.getsize(mp3_path) > 0:
                    out_item["mp3Url"] = output["mp3Url"]
                    db.add(models.TemporaryFile(
                        processing_request_id=db_req.id,
                        file_type=f"{output['key']}_mp3",
                        storage_path=mp3_path,
                        expires_at=expires,
                        created_at=now
                    ))
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
    original_mode: str = Form(default="")
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

    import numpy as np
    
    dir_val = parse_and_clamp(direccion, -180.0, 180.0, 0.0)
    alt_val = parse_and_clamp(altura, -90.0, 90.0, 0.0)
    ape_val = parse_and_clamp(apertura, 0.0, 100.0, 0.0)
    mov_val = parse_and_clamp(movimiento, 0.0, 100.0, 0.0)
    
    orig_mode_bool = False
    if original_mode and str(original_mode).strip().lower() in ["true", "1", "yes"]:
        orig_mode_bool = True
    # --------------------------------

    session_id = str(uuid.uuid4())
    session_dir = os.path.join(STATIC_DIR, session_id)
    os.makedirs(session_dir, exist_ok=True)
    
    # Save audio input
    file_ext = os.path.splitext(audio.filename)[1].lower() if audio.filename else ".wav"
    if not file_ext or file_ext not in [".wav", ".mp3"]:
        shutil.rmtree(session_dir, ignore_errors=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato no soportado ({file_ext}). Solo se admiten archivos WAV o MP3."
        )
    input_path = os.path.join(session_dir, f"input{file_ext}")

    logger.info(f"Guardando input audio en {input_path}")
    with open(input_path, "wb") as f:
        shutil.copyfileobj(audio.file, f)

    # Validar formato y frecuencia de muestreo admitida (44.1, 48 o 96 kHz sin remuestreo)
    try:
        info = sf.info(input_path)
        input_sr = info.samplerate
    except Exception as e:
        logger.warning(f"Error al leer audio en demo: {e}")
        shutil.rmtree(session_dir, ignore_errors=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo procesar el archivo de audio. Verifica que sea un WAV o MP3 válido."
        )

    try:
        validated_sr = validate_sample_rate(input_sr)
    except ValueError as ve:
        logger.warning(f"Audio rechazado en demo por frecuencia de muestreo no admitida: {ve}")
        shutil.rmtree(session_dir, ignore_errors=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )

    hrtf_sr, pos_sr = get_sofa_for_sr(validated_sr)

    logger.info(f"Ejecutando procesamiento nativo de demo en worker thread con params: dir={dir_val}, alt={alt_val}, ap={ape_val}, mov={mov_val} (sr={validated_sr} Hz)")
    try:
        async with dsp_semaphore:
            await asyncio.to_thread(
                native_process_demo,
                input_path=input_path,
                output_dir=session_dir,
                direccion=dir_val,
                altura=alt_val,
                apertura=ape_val,
                movimiento=mov_val,
                hrtf=hrtf_sr,
                pos=pos_sr,
                original_mode=orig_mode_bool
            )
    except ValueError as ve:
        logger.warning(f"Validación en demo fallida: {ve}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
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
        p_mp3 = os.path.join(session_dir, "preview_binaural.mp3")
        if os.path.exists(p_mp3) and os.path.getsize(p_mp3) > 0:
            res["binaural"]["mp3Url"] = binaural_mp3
    if os.path.exists(os.path.join(session_dir, "preview_3d_perceptual.wav")):
        res["binaural_3d"]["wavUrl"] = perceptual_wav
        p3d_mp3 = os.path.join(session_dir, "preview_3d_perceptual.mp3")
        if os.path.exists(p3d_mp3) and os.path.getsize(p3d_mp3) > 0:
            res["binaural_3d"]["mp3Url"] = perceptual_mp3

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
