# routers/conversions.py
from __future__ import annotations


import logging
import time
from pathlib import Path
from typing import List, Optional
from uuid import UUID

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
)
from fastapi.responses import FileResponse
from sqlalchemy import desc
from sqlalchemy.orm import Session

from database import SessionLocal, get_db
from models import AudioFile, ConversionJob, VisitorSession
from schemas import ConvertRequest, ConversionJobOut
from services.conversion_service import stereo_to_foa_placeholder


logger = logging.getLogger(__name__)

router = APIRouter(tags=["conversion"])


# Estados posibles del trabajo de conversión.
PENDING = "pending"
PROCESSING = "processing"
COMPLETED = "completed"
FAILED = "failed"


# Carpeta en la que actualmente se guardan los resultados.
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


# =========================================================
# CREAR CONVERSIÓN
# =========================================================

@router.post(
    "/convert",
    response_model=ConversionJobOut,
    status_code=202,
)
def convert(
    req: ConvertRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Crea una solicitud de conversión.

    La conversión solamente se permite cuando:

    1. La sesión indicada existe.
    2. El audio existe.
    3. El audio pertenece a esa misma sesión.
    4. El archivo original existe en el almacenamiento.
    """

    # 1. Buscar y validar la sesión recibida.
    visitor_session = (
        db.query(VisitorSession)
        .filter(
            VisitorSession.session_token == req.session_token
        )
        .first()
    )

    if visitor_session is None:
        raise HTTPException(
            status_code=404,
            detail="La sesión indicada no existe",
        )

    # 2. Buscar el audio comprobando al mismo tiempo
    # que pertenece a la sesión indicada.
    audio = (
        db.query(AudioFile)
        .filter(
            AudioFile.id == req.audio_file_id,
            AudioFile.session_id == visitor_session.id,
        )
        .first()
    )

    if audio is None:
        raise HTTPException(
            status_code=404,
            detail="Audio no encontrado para esta sesión",
        )

    # 3. Normalizar y verificar la ruta del archivo original.
    safe_input_path = (
        audio.upload_path
        .lstrip("/\\")
        .replace("\\", "/")
    )

    input_path = Path(safe_input_path)

    if not input_path.exists():
        raise HTTPException(
            status_code=404,
            detail=(
                "El archivo de audio no existe "
                "en el almacenamiento"
            ),
        )

    # 4. Crear el registro del trabajo de conversión.
    job = ConversionJob(
        audio_file_id=audio.id,
        session_id=visitor_session.id,
        ambisonics_format=req.ambisonics_format,
        processing_mode=req.processing_mode,
        status=PENDING,
        processing_time=None,
        output_path=None,
        error_message=None,
        output_duration_seconds=None,
        total_time_seconds=None,
        dsp_time_seconds=None,
        peak_memory_mb=None,
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    # 5. Lanzar el procesamiento en segundo plano.
    # FastAPI responde primero con código 202 y después
    # ejecuta run_job().
    background_tasks.add_task(
        run_job,
        job.id,
    )

    return job


# =========================================================
# CONSULTAR UN TRABAJO
# =========================================================

@router.get(
    "/jobs/{job_id}",
    response_model=ConversionJobOut,
)
def get_job(
    job_id: int,
    session_token: UUID,
    db: Session = Depends(get_db),
):
    """
    Consulta un trabajo de conversión únicamente cuando
    pertenece a la sesión visitante indicada.
    """

    # 1. Comprobar que la sesión exista.
    visitor_session = (
        db.query(VisitorSession)
        .filter(
            VisitorSession.session_token == session_token
        )
        .first()
    )

    if visitor_session is None:
        raise HTTPException(
            status_code=404,
            detail="La sesión indicada no existe",
        )

    # 2. Buscar el trabajo verificando que pertenezca
    # a la misma sesión.
    job = (
        db.query(ConversionJob)
        .filter(
            ConversionJob.id == job_id,
            ConversionJob.session_id == visitor_session.id,
        )
        .first()
    )

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Conversión no encontrada para esta sesión",
        )

    return job


# =========================================================
# LISTAR TRABAJOS
# =========================================================

@router.get(
    "/jobs",
    response_model=List[ConversionJobOut],
)
def list_jobs(
    session_token: UUID,
    audio_file_id: Optional[int] = None,
    status: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """
    Lista únicamente los trabajos de conversión asociados
    con la sesión visitante indicada.

    Permite filtrar adicionalmente por:

    - audio_file_id
    - status
    """

    # 1. Comprobar que la sesión exista.
    visitor_session = (
        db.query(VisitorSession)
        .filter(
            VisitorSession.session_token == session_token
        )
        .first()
    )

    if visitor_session is None:
        raise HTTPException(
            status_code=404,
            detail="La sesión indicada no existe",
        )

    # 2. Consultar únicamente los trabajos de esa sesión.
    query = db.query(ConversionJob).filter(
        ConversionJob.session_id == visitor_session.id
    )

    # 3. Aplicar filtros opcionales sin eliminar
    # la restricción principal por sesión.
    if audio_file_id is not None:
        query = query.filter(
            ConversionJob.audio_file_id == audio_file_id
        )

    if status is not None:
        query = query.filter(
            ConversionJob.status == status.lower()
        )

    return (
        query
        .order_by(desc(ConversionJob.id))
        .limit(limit)
        .all()
    )

# =========================================================
# DESCARGAR RESULTADO
# =========================================================

@router.get("/jobs/{job_id}/download")
def download_job_output(
    job_id: int,
    session_token: UUID,
    db: Session = Depends(get_db),
):
    """
    Descarga el resultado de una conversión únicamente cuando:

    1. La sesión existe.
    2. La conversión pertenece a esa sesión.
    3. El procesamiento terminó correctamente.
    4. El archivo de salida existe.
    """

    # 1. Validar la sesión visitante.
    visitor_session = (
        db.query(VisitorSession)
        .filter(
            VisitorSession.session_token == session_token
        )
        .first()
    )

    if visitor_session is None:
        raise HTTPException(
            status_code=404,
            detail="La sesión indicada no existe",
        )

    # 2. Buscar el trabajo y comprobar su pertenencia.
    job = (
        db.query(ConversionJob)
        .filter(
            ConversionJob.id == job_id,
            ConversionJob.session_id == visitor_session.id,
        )
        .first()
    )

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Conversión no encontrada para esta sesión",
        )

    # 3. Comprobar que la conversión haya terminado.
    if job.status != COMPLETED:
        raise HTTPException(
            status_code=400,
            detail=(
                "La conversión todavía no está completada. "
                f"Estado actual: {job.status}"
            ),
        )

    # 4. Comprobar que exista una ruta de salida.
    if not job.output_path:
        raise HTTPException(
            status_code=404,
            detail="La conversión no tiene un archivo de salida",
        )

    # 5. Normalizar la ruta guardada.
    safe_output_path = (
        job.output_path
        .lstrip("/\\")
        .replace("\\", "/")
    )

    output_path = Path(safe_output_path)

    # 6. Comprobar que el archivo exista físicamente.
    if not output_path.exists():
        raise HTTPException(
            status_code=404,
            detail=(
                "El archivo convertido no existe "
                "en el almacenamiento"
            ),
        )

    # 7. Entregar el archivo después de validar el acceso.
    return FileResponse(
        path=str(output_path),
        media_type="audio/wav",
        filename=output_path.name,
    )

# =========================================================
# PROCESAMIENTO EN SEGUNDO PLANO
# =========================================================

def run_job(job_id: int) -> None:
    """
    Ejecuta la conversión en segundo plano.

    Actualmente utiliza stereo_to_foa_placeholder().
    Posteriormente esta llamada se reemplazará por la
    integración con el backend DSP real.

    Se crea una nueva sesión de base de datos porque
    esta función se ejecuta después de terminar la
    solicitud HTTP original.
    """

    db = SessionLocal()

    try:
        # 1. Buscar el trabajo.
        job = db.get(ConversionJob, job_id)

        if not job:
            return

        # 2. Buscar el audio relacionado.
        audio = db.get(
            AudioFile,
            job.audio_file_id,
        )

        if not audio:
            job.status = FAILED
            job.error_message = (
                "El audio asociado no existe"
            )
            db.commit()
            return

        # 3. Comprobar el archivo original.
        safe_input_path = (
            audio.upload_path
            .lstrip("/\\")
            .replace("\\", "/")
        )

        input_path = Path(safe_input_path)

        if not input_path.exists():
            job.status = FAILED
            job.error_message = (
                "El archivo de entrada no existe: "
                f"{input_path}"
            )
            db.commit()
            return

        # 4. Cambiar el trabajo a processing.
        job.status = PROCESSING
        job.error_message = None
        db.commit()

        # 5. Construir el nombre del archivo de salida.
        stem = Path(
            audio.original_filename
        ).stem

        output_path = OUTPUT_DIR / (
            f"job_{job.id}_"
            f"{stem}_"
            f"{job.ambisonics_format}.wav"
        )

        # 6. Medir el tiempo utilizado por el placeholder.
        start_time = time.perf_counter()

        stereo_to_foa_placeholder(
            str(input_path),
            str(output_path),
        )

        end_time = time.perf_counter()

        # 7. Guardar el resultado del procesamiento.
        job.output_path = output_path.as_posix()
        job.processing_time = round(
            end_time - start_time,
            4,
        )
        job.status = COMPLETED
        job.error_message = None

        db.commit()

    except Exception as exc:
        logger.exception(
            "Error en run_job(job_id=%s)",
            job_id,
        )

        try:
            job = db.get(
                ConversionJob,
                job_id,
            )

            if job:
                job.status = FAILED
                job.error_message = str(exc)[:500]
                db.commit()

        except Exception:
            db.rollback()

    finally:
        db.close()