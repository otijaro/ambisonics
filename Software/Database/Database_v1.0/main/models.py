from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    REAL,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    username = Column(
        String(50),
        unique=True,
        nullable=False,
    )

    email = Column(
        String(255),
        unique=True,
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=True,
    )


class AudioFile(Base):
    __tablename__ = "audio_files"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    user_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    session_id = Column(
    	BigInteger,
    	ForeignKey(
        	"visitor_sessions.id",
        	ondelete="SET NULL",
    ),
    nullable=True,
    index=True,
    )

    original_filename = Column(
        String(255),
        nullable=False,
    )

    file_format = Column(
        String(20),
        nullable=False,
    )

    sample_rate = Column(
        Integer,
        nullable=True,
    )

    duration_seconds = Column(
        REAL,
        nullable=True,
    )

    upload_path = Column(
        Text,
        nullable=False,
    )

    uploaded_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=True,
    )


class ConversionJob(Base):
    __tablename__ = "conversion_jobs"

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'processing', 'completed', 'failed')",
            name="conversion_jobs_status_check",
        ),
        CheckConstraint(
            "output_duration_seconds IS NULL "
            "OR output_duration_seconds >= 0",
            name="conversion_jobs_output_duration_check",
        ),
        CheckConstraint(
            "total_time_seconds IS NULL "
            "OR total_time_seconds >= 0",
            name="conversion_jobs_total_time_check",
        ),
        CheckConstraint(
            "dsp_time_seconds IS NULL "
            "OR dsp_time_seconds >= 0",
            name="conversion_jobs_dsp_time_check",
        ),
        CheckConstraint(
            "peak_memory_mb IS NULL "
            "OR peak_memory_mb >= 0",
            name="conversion_jobs_peak_memory_check",
        ),
        CheckConstraint(
            "processing_mode IS NULL "
            "OR processing_mode IN ('memory', 'streaming')",
            name="conversion_jobs_processing_mode_check",
        ),
    )

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    audio_file_id = Column(
        BigInteger,
        ForeignKey("audio_files.id", ondelete="CASCADE"),
        nullable=True,
    )

    session_id = Column(
        BigInteger,
        ForeignKey("visitor_sessions.id", ondelete="SET NULL"),
        nullable=True,
    )

    ambisonics_format = Column(
        String(20),
        server_default="ACN_SN3D",
        nullable=True,
    )

    status = Column(
        String(20),
        nullable=True,
    )

    # Campo anterior: se conserva para no romper el backend actual.
    processing_time = Column(
        REAL,
        nullable=True,
    )

    output_path = Column(
        Text,
        nullable=True,
    )

    error_message = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=True,
    )

    finished_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    output_duration_seconds = Column(
        REAL,
        nullable=True,
    )

    total_time_seconds = Column(
        REAL,
        nullable=True,
    )

    dsp_time_seconds = Column(
        REAL,
        nullable=True,
    )

    peak_memory_mb = Column(
        REAL,
        nullable=True,
    )

    processing_mode = Column(
        String(20),
        nullable=True,
    )


class VisitorSession(Base):
    __tablename__ = "visitor_sessions"

    __table_args__ = (
        CheckConstraint(
            "usage_seconds >= 0",
            name="visitor_sessions_usage_seconds_check",
        ),
    )

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    session_token = Column(
        UUID(as_uuid=True),
        unique=True,
        nullable=False,
    )

    entry_time = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    last_activity_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    exit_time = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    usage_seconds = Column(
        Integer,
        server_default="0",
        nullable=False,
    )


class Suggestion(Base):
    __tablename__ = "suggestions"

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    session_id = Column(
        BigInteger,
        ForeignKey("visitor_sessions.id"),
        nullable=False,
    )

    name = Column(
        String(100),
        nullable=False,
    )

    email = Column(
        String(255),
        nullable=False,
    )

    message = Column(
        Text,
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
