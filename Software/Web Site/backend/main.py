import os
import uuid
import json
import logging
import shutil
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.processor import convert_audio as native_convert_audio, process_demo as native_process_demo
from backend.core_dsp import load_sofa

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
    
    yield
    
    # Shutdown logic
    logger.info("Apagando servidor...")
    app_state["hrtf"] = None
    app_state["pos"] = None

app = FastAPI(title="Ambisonic Backend", lifespan=lifespan)

# Enable CORS for Next.js frontend (typically port 3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ambisonic.vercel.app",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static folder to serve generated audio files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}

@app.post("/api/convert")
async def convert_audio(
    audio: UploadFile = File(...),
    mode: str = Form("auto")
):
    session_id = str(uuid.uuid4())
    session_dir = os.path.join(STATIC_DIR, session_id)
    os.makedirs(session_dir, exist_ok=True)

    # Save incoming audio file
    file_ext = os.path.splitext(audio.filename)[1]
    if not file_ext:
        file_ext = ".wav"  # fallback
    input_path = os.path.join(session_dir, f"input{file_ext}")

    logger.info(f"Guardando input audio en {input_path}")
    with open(input_path, "wb") as f:
        shutil.copyfileobj(audio.file, f)

    # Ejecutar procesamiento nativo
    logger.info(f"Ejecutando procesamiento nativo de conversión con modo {mode}")
    try:
        original_duration, proc_time = native_convert_audio(
            input_path=input_path,
            output_dir=session_dir,
            mode=mode,
            hrtf=app_state["hrtf"],
            pos=app_state["pos"]
        )
    except Exception as e:
        logger.error(f"Error executing native convert: {str(e)}")
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
        },
        {
            "key": "cuad_horizontal",
            "wavUrl": f"/static/{session_id}/output_4_speakers_horizontal_FLBR.wav"
        },
        {
            "key": "cuad_altura",
            "wavUrl": f"/static/{session_id}/output_4_speakers_altura_FLRT.wav"
        },
        {
            "key": "horizontal_3d",
            "wavUrl": f"/static/{session_id}/output_4_speakers_horizontal_3D_FLBR.wav"
        },
        {
            "key": "altura_3d",
            "wavUrl": f"/static/{session_id}/output_4_speakers_altura_3D_FLRT.wav"
        }
    ]

    # Verify that files were created
    available_outputs = []
    for output in outputs:
        # Check wav exists
        wav_filename = os.path.basename(output["wavUrl"])
        wav_path = os.path.join(session_dir, wav_filename)
        if os.path.exists(wav_path):
            out_item = {"key": output["key"], "wavUrl": output["wavUrl"]}
            if "mp3Url" in output:
                # El MP3 se genera asíncronamente, por lo que asumimos que existirá
                out_item["mp3Url"] = output["mp3Url"]
            available_outputs.append(out_item)

    logger.info(f"Conversion completa. Archivos disponibles: {len(available_outputs)}.")
    return {
        "outputs": available_outputs,
        "processing_seconds": proc_time,
        "original_duration_seconds": original_duration
    }

@app.post("/api/demo")
async def run_demo_notebook(
    audio: UploadFile = File(...),
    direccion: float = Form(...),
    altura: float = Form(...),
    apertura: float = Form(...),
    movimiento: float = Form(...)
):
    session_id = str(uuid.uuid4())
    session_dir = os.path.join(STATIC_DIR, session_id)
    os.makedirs(session_dir, exist_ok=True)
    
    # Save audio input
    file_ext = os.path.splitext(audio.filename)[1]
    if not file_ext:
        file_ext = ".wav"
    input_path = os.path.join(session_dir, f"input{file_ext}")

    logger.info(f"Guardando input audio en {input_path}")
    with open(input_path, "wb") as f:
        shutil.copyfileobj(audio.file, f)

    logger.info(f"Ejecutando procesamiento nativo de demo con params: dir={direccion}, alt={altura}, ap={apertura}, mov={movimiento}")
    try:
        native_process_demo(
            input_path=input_path,
            output_dir=session_dir,
            direccion=direccion,
            altura=altura,
            apertura=apertura,
            movimiento=movimiento,
            hrtf=app_state["hrtf"],
            pos=app_state["pos"]
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
async def save_feedback(payload: FeedbackPayload):
    try:
        feedback_list = []
        if os.path.exists(FEEDBACK_FILE):
            with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
                try:
                    feedback_list = json.load(f)
                except Exception:
                    pass

        feedback_list.append({
            "nombre": payload.nombre,
            "correo": payload.correo,
            "mensaje": payload.mensaje,
            "id": str(uuid.uuid4())
        })

        with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
            json.dump(feedback_list, f, indent=4, ensure_ascii=False)

        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error saving feedback: {str(e)}")
        raise HTTPException(status_code=500, detail="No se pudo guardar la sugerencia.")
