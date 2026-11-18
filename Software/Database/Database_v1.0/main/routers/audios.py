# routers/audios.py
from __future__ import annotations
from uuid import UUID

from pathlib import Path
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import desc
from sqlalchemy.orm import Session

from database import get_db
from models import AudioFile, VisitorSession
from schemas import AudioFileOut

router = APIRouter(tags=["audios"])


@router.get("/audios", response_model=List[AudioFileOut])
def list_audios(
    session_token: UUID,
    file_format: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """
    Lista únicamente los audios asociados con la sesión visitante
    identificada mediante session_token.
    """

    # Buscar la sesión recibida.
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

    # Consultar solamente los audios de esa sesión.
    query = db.query(AudioFile).filter(
        AudioFile.session_id == visitor_session.id
    )

    if file_format is not None:
        query = query.filter(
            AudioFile.file_format == file_format.lower()
        )

    return (
        query
        .order_by(desc(AudioFile.id))
        .limit(limit)
        .all()
    )

@router.get("/audios/{audio_id}", response_model=AudioFileOut)
def get_audio(
    audio_id: int,
    session_token: UUID,
    db: Session = Depends(get_db),
):
    """
    Obtiene la información de un audio únicamente cuando
    pertenece a la sesión visitante indicada.
    """

    # 1. Validar que la sesión exista.
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

    # 2. Buscar simultáneamente el audio y su propietario temporal.
    audio = (
        db.query(AudioFile)
        .filter(
            AudioFile.id == audio_id,
            AudioFile.session_id == visitor_session.id,
        )
        .first()
    )

    if audio is None:
        raise HTTPException(
            status_code=404,
            detail="Audio no encontrado para esta sesión",
        )

    return audio

@router.get("/audios/{audio_id}/download")
def download_audio(
    audio_id: int,
    session_token: UUID,
    db: Session = Depends(get_db),
):
    """
    Descarga el archivo original únicamente cuando pertenece
    a la sesión visitante indicada.
    """

    # 1. Validar que la sesión exista.
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

    # 2. Buscar el audio verificando simultáneamente su propietario temporal.
    audio = (
        db.query(AudioFile)
        .filter(
            AudioFile.id == audio_id,
            AudioFile.session_id == visitor_session.id,
        )
        .first()
    )

    if audio is None:
        raise HTTPException(
            status_code=404,
            detail="Audio no encontrado para esta sesión",
        )

    # 3. Verificar que el registro tenga una ruta guardada.
    if not audio.upload_path:
        raise HTTPException(
            status_code=404,
            detail="Este audio no tiene un archivo asociado",
        )

    # 4. Normalizar la ruta almacenada.
    safe_path = audio.upload_path.lstrip("/\\").replace("\\", "/")
    input_path = Path(safe_path)

    # 5. Comprobar que el archivo exista físicamente.
    if not input_path.exists():
        raise HTTPException(
            status_code=404,
            detail="El archivo de audio no existe en el almacenamiento",
        )

    # 6. Entregar el archivo únicamente después de validar la propiedad.
    return FileResponse(
        path=str(input_path),
        media_type="audio/wav",
        filename=audio.original_filename,
    )