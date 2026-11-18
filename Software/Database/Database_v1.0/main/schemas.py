# schemas.py
from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

class ConvertRequest(BaseModel):
    audio_file_id: int = Field(
        ...,
        ge=1,
        description="ID del audio previamente subido",
    )

    session_token: UUID = Field(
        ...,
        description="Token UUID de la sesión del visitante",
    )

    ambisonics_format: str = Field(
        "ACN_SN3D",
        description="Formato ambisónico objetivo",
    )

    processing_mode: Optional[
        Literal["memory", "streaming"]
    ] = Field(
        None,
        description="Modo de procesamiento utilizado por el backend DSP",
    )

class ConversionJobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int

    audio_file_id: Optional[int] = None
    session_id: Optional[int] = None

    ambisonics_format: Optional[str] = None
    status: Optional[str] = None

    # Campo antiguo conservado por compatibilidad.
    processing_time: Optional[float] = None

    output_path: Optional[str] = None
    error_message: Optional[str] = None

    created_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None

    output_duration_seconds: Optional[float] = None
    total_time_seconds: Optional[float] = None
    dsp_time_seconds: Optional[float] = None
    peak_memory_mb: Optional[float] = None

    processing_mode: Optional[
        Literal["memory", "streaming"]
    ] = None

class AudioFileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: Optional[int] = None
    session_id: Optional[int] = None
    original_filename: str
    file_format: str
    sample_rate: Optional[int] = None
    duration_seconds: Optional[float] = None
    upload_path: str
    uploaded_at: Optional[datetime] = None

class VisitorSessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_token: UUID
    entry_time: datetime
    last_activity_at: datetime
    exit_time: Optional[datetime] = None
    usage_seconds: int

class SuggestionCreate(BaseModel):
    session_token: UUID

    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Nombre de la persona que envía la sugerencia",
    )

    email: str = Field(
        ...,
        min_length=5,
        max_length=255,
        pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
        description="Correo electrónico de contacto",
    )

    message: str = Field(
        ...,
        min_length=5,
        max_length=2000,
        description="Contenido de la sugerencia",
    )


class SuggestionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: int
    name: str
    email: str
    message: str
    created_at: datetime