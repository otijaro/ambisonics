from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator

from pydantic import BaseModel, ConfigDict, Field, model_validator, EmailStr

class UserCreate(BaseModel):
    name: str = Field(..., max_length=120)
    email: EmailStr
    password: str = Field(..., min_length=8)
    consent_given: bool

    @model_validator(mode="before")
    @classmethod
    def require_consent(cls, values: dict) -> dict:
        if isinstance(values, dict):
            if not values.get("consent_given"):
                raise ValueError("El consentimiento de tratamiento de datos es obligatorio.")
            
            email = values.get("email")
            if isinstance(email, str):
                values["email"] = email.strip().casefold()
                
            name = values.get("name")
            if isinstance(name, str):
                values["name"] = name.strip()
        return values

class UserLogin(BaseModel):
    email: EmailStr
    password: str

    @model_validator(mode="before")
    @classmethod
    def normalize_email(cls, values: dict) -> dict:
        if isinstance(values, dict):
            email = values.get("email")
            if isinstance(email, str):
                values["email"] = email.strip().casefold()
        return values

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    created_at: datetime

class RegisterResponse(BaseModel):
    message: str
    recovery_code: str

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str

    @model_validator(mode="after")
    def check_passwords_match(self) -> "PasswordChangeRequest":
        if self.new_password != self.confirm_password:
            raise ValueError("Las contraseñas no coinciden.")
        return self

class PasswordResetRequest(BaseModel):
    email: EmailStr
    recovery_code: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str

    @model_validator(mode="before")
    @classmethod
    def normalize_email(cls, values: dict) -> dict:
        if isinstance(values, dict):
            email = values.get("email")
            if isinstance(email, str):
                values["email"] = email.strip().casefold()
        return values

    @model_validator(mode="after")
    def check_passwords_match(self) -> "PasswordResetRequest":
        if self.new_password != self.confirm_password:
            raise ValueError("Las contraseñas no coinciden.")
        return self

class PasswordResetResponse(BaseModel):
    message: str
    new_recovery_code: str

class GenerateRecoveryCodeResponse(BaseModel):
    message: str
    recovery_code: str

class ProcessingRequestCreate(BaseModel):
    original_filename: str = Field(..., description="Nombre original del archivo cargado")
    input_mode: Literal["stereo", "tetra_4mic"] = Field(..., description="Modo de entrada de audio")

class ProcessingRequestUpdate(BaseModel):
    status: Optional[Literal["processing", "completed", "failed"]] = None
    processing_sample_rate_hz: Optional[int] = Field(None, gt=0)
    original_duration_seconds: Optional[float] = Field(None, ge=0)
    processing_seconds: Optional[float] = Field(None, ge=0)
    processing_percentage: Optional[float] = Field(None, ge=0)
    finished_at: Optional[datetime] = None
    error_message: Optional[str] = None

class ProcessingRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    original_filename: str
    input_mode: str
    status: str
    processing_sample_rate_hz: Optional[int] = None
    original_duration_seconds: Optional[float] = None
    processing_seconds: Optional[float] = None
    processing_percentage: Optional[float] = None
    requested_at: datetime
    finished_at: Optional[datetime] = None
    error_message: Optional[str] = None

class ProcessingRequestFile(BaseModel):
    file_type: str

class ProcessingRequestMineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    original_filename: str
    input_mode: str
    status: str
    requested_at: datetime
    finished_at: Optional[datetime] = None
    processing_sample_rate_hz: Optional[int] = None
    original_duration_seconds: Optional[float] = None
    processing_seconds: Optional[float] = None
    processing_percentage: Optional[float] = None
    file_status: str
    is_available: bool
    files: list[ProcessingRequestFile] = []

class SuggestionCreate(BaseModel):
    name: Optional[str] = Field(None, max_length=120)
    email: Optional[str] = Field(None, max_length=254)
    message: str = Field(..., min_length=1)
    consent_given: bool = False

    @model_validator(mode="before")
    @classmethod
    def normalize_empty_strings(cls, values: dict) -> dict:
        if isinstance(values, dict):
            name = values.get("name")
            if isinstance(name, str):
                name = name.strip()
                values["name"] = name if name else None

            email = values.get("email")
            if isinstance(email, str):
                email = email.strip()
                values["email"] = email if email else None
        return values

class Suggestion(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: Optional[str] = None
    email: Optional[str] = None
    message: str
    consent_given: bool
    created_at: datetime