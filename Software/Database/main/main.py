# =====================
# IMPORTS
# =====================
import os
import shutil
from pathlib import Path
from uuid import UUID

import soundfile as sf
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware

from database import SessionLocal
from models import AudioFile, VisitorSession
from routers.audios import router as audios_router
from routers.conversions import router as conversions_router
from routers.sessions import router as sessions_router
from routers.suggestions import router as suggestions_router


# =====================
# CONFIGURACIÓN
# =====================
load_dotenv()

DEFAULT_FRONTEND_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# Permite configurar uno o varios orígenes separados por comas desde .env.
# Ejemplo:
# FRONTEND_ORIGINS=http://localhost:3000,https://mi-proyecto.vercel.app
frontend_origins_env = os.getenv("FRONTEND_ORIGINS", "").strip()

if frontend_origins_env:
    allowed_origins = [
        origin.strip().rstrip("/")
        for origin in frontend_origins_env.split(",")
        if origin.strip()
    ]
else:
    allowed_origins = DEFAULT_FRONTEND_ORIGINS

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# =====================
# APLICACIÓN FASTAPI
# =====================
app = FastAPI(
    title="Ambisonics Backend",
    description=(
        "API para registrar sesiones visitantes, cargar audios, "
        "gestionar conversiones ambisónicas y recibir sugerencias."
    ),
    version="1.3",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(conversions_router)
app.include_router(audios_router)
app.include_router(sessions_router)
app.include_router(suggestions_router)


# =====================
# ENDPOINT DE ESTADO
# =====================
@app.get("/")
def root():
    """Comprueba que el backend está disponible."""
    return {
        "status": "Backend funcionando",
        "version": "1.3",
    }


# =====================
# CARGA DE AUDIO
# =====================
@app.post("/upload", status_code=status.HTTP_201_CREATED)
def upload_audio(
    session_token: UUID = Form(...),
    file: UploadFile = File(...),
):
    """
    Guarda un audio subido por un visitante y lo relaciona
    con la sesión identificada mediante ``session_token``.

    En esta etapa del proyecto, los visitantes no tienen una cuenta,
    por lo que ``user_id`` permanece en NULL y la propiedad temporal
    del archivo se controla mediante ``session_id``.
    """

    db = SessionLocal()
    file_path: Path | None = None
    committed = False

    try:
        # 1. Validar que la sesión visitante exista.
        visitor_session = (
            db.query(VisitorSession)
            .filter(
                VisitorSession.session_token == session_token
            )
            .first()
        )

        if visitor_session is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La sesión indicada no existe",
            )

        # 2. Validar y normalizar el nombre recibido.
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El archivo no tiene un nombre válido",
            )

        safe_filename = Path(file.filename).name
        file_extension = Path(safe_filename).suffix.lower().lstrip(".")

        if not safe_filename or not file_extension:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El archivo debe tener una extensión válida",
            )

        # 3. Guardar físicamente el archivo.
        file_path = UPLOAD_DIR / safe_filename

        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 4. Leer la metadata técnica sin cargar todo el audio en memoria.
        try:
            audio_info = sf.info(str(file_path))
        except RuntimeError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El archivo no pudo ser interpretado como audio válido",
            ) from exc

        # 5. Crear el registro en PostgreSQL.
        audio = AudioFile(
            user_id=None,
            session_id=visitor_session.id,
            original_filename=safe_filename,
            file_format=file_extension,
            sample_rate=int(audio_info.samplerate),
            duration_seconds=float(audio_info.duration),
            upload_path=file_path.as_posix(),
        )

        db.add(audio)
        db.commit()
        committed = True
        db.refresh(audio)

        # 6. Devolver la información necesaria para el frontend.
        return {
            "audio_file_id": audio.id,
            "user_id": audio.user_id,
            "session_id": audio.session_id,
            "filename": audio.original_filename,
            "file_format": audio.file_format,
            "sample_rate": audio.sample_rate,
            "duration_seconds": audio.duration_seconds,
            "upload_path": audio.upload_path,
        }

    except HTTPException:
        db.rollback()

        if file_path is not None and file_path.exists() and not committed:
            file_path.unlink(missing_ok=True)

        raise

    except Exception as exc:
        db.rollback()

        if file_path is not None and file_path.exists() and not committed:
            file_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No fue posible registrar el archivo de audio",
        ) from exc

    finally:
        file.file.close()
        db.close()
