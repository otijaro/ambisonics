from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Double,
    Integer,
    String,
    Text,
    ForeignKey,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from backend.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(120), nullable=False)
    email = Column(String(254), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    consent_given = Column(Boolean, nullable=False, default=False)
    consent_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    recovery_code_hash = Column(String(255), nullable=True)
    
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")

class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_hash = Column(String(255), nullable=False, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_activity_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="sessions")

class ProcessingRequest(Base):
    __tablename__ = "processing_requests"

    __table_args__ = (
        CheckConstraint(
            "input_mode IN ('stereo', 'tetra_4mic')",
            name="processing_requests_input_mode_check"
        ),
        CheckConstraint(
            "status IN ('processing', 'completed', 'failed')",
            name="processing_requests_status_check"
        ),
        CheckConstraint(
            "processing_sample_rate_hz IS NULL OR processing_sample_rate_hz > 0",
            name="processing_requests_sample_rate_check"
        ),
        CheckConstraint(
            "original_duration_seconds IS NULL OR original_duration_seconds >= 0",
            name="processing_requests_original_duration_check"
        ),
        CheckConstraint(
            "processing_seconds IS NULL OR processing_seconds >= 0",
            name="processing_requests_processing_seconds_check"
        ),
        CheckConstraint(
            "processing_percentage IS NULL OR processing_percentage >= 0",
            name="processing_requests_processing_percentage_check"
        ),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    original_filename = Column(Text, nullable=False)
    input_mode = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False)
    processing_sample_rate_hz = Column(Integer, nullable=True)
    original_duration_seconds = Column(Double, nullable=True)
    processing_seconds = Column(Double, nullable=True)
    processing_percentage = Column(Double, nullable=True)
    requested_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)


class Suggestion(Base):
    __tablename__ = "suggestions"

    __table_args__ = (
        CheckConstraint(
            "(name IS NULL AND email IS NULL) OR consent_given = TRUE",
            name="suggestions_privacy_check"
        ),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(120), nullable=True)
    email = Column(String(254), nullable=True)
    message = Column(Text, nullable=False)
    consent_given = Column(Boolean, nullable=False, server_default="false")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

class TemporaryFile(Base):
    __tablename__ = "temporary_files"

    __table_args__ = (
        CheckConstraint(
            "expires_at > created_at",
            name="temporary_files_expiration_check"
        ),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    processing_request_id = Column(BigInteger, ForeignKey("processing_requests.id", ondelete="CASCADE"), nullable=False)
    file_type = Column(String(30), nullable=False)
    storage_path = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

