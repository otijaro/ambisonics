# routers/sessions.py

from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import VisitorSession
from schemas import VisitorSessionOut


router = APIRouter(
    prefix="/sessions",
    tags=["sessions"],
)


def get_session_or_404(
    session_token: UUID,
    db: Session,
) -> VisitorSession:
    """
    Busca una sesión mediante su token UUID.
    Si no existe, devuelve un error 404.
    """
    visitor_session = (
        db.query(VisitorSession)
        .filter(VisitorSession.session_token == session_token)
        .first()
    )

    if visitor_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La sesión indicada no existe",
        )

    return visitor_session


@router.post(
    "/start",
    response_model=VisitorSessionOut,
    status_code=status.HTTP_201_CREATED,
)
def start_session(
    db: Session = Depends(get_db),
):
    """
    Crea una nueva sesión cuando una persona entra a la página.
    """
    visitor_session = VisitorSession(
        session_token=uuid4(),
    )

    db.add(visitor_session)
    db.commit()
    db.refresh(visitor_session)

    return visitor_session


@router.get(
    "/{session_token}",
    response_model=VisitorSessionOut,
)
def get_session(
    session_token: UUID,
    db: Session = Depends(get_db),
):
    """
    Consulta una sesión y permite conocer su id interno.
    """
    return get_session_or_404(session_token, db)


@router.patch(
    "/{session_token}/activity",
    response_model=VisitorSessionOut,
)
def update_session_activity(
    session_token: UUID,
    db: Session = Depends(get_db),
):
    """
    Actualiza la última actividad y el tiempo de uso acumulado.
    """
    visitor_session = get_session_or_404(session_token, db)

    if visitor_session.exit_time is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La sesión ya fue finalizada",
        )

    now = datetime.now(timezone.utc)

    visitor_session.last_activity_at = now
    visitor_session.usage_seconds = max(
        0,
        int((now - visitor_session.entry_time).total_seconds()),
    )

    db.commit()
    db.refresh(visitor_session)

    return visitor_session


@router.post(
    "/{session_token}/end",
    response_model=VisitorSessionOut,
)
def end_session(
    session_token: UUID,
    db: Session = Depends(get_db),
):
    """
    Guarda la hora de salida y calcula el tiempo total de uso.
    """
    visitor_session = get_session_or_404(session_token, db)

    # Si ya terminó, devuelve el registro existente sin duplicar el cierre.
    if visitor_session.exit_time is not None:
        return visitor_session

    now = datetime.now(timezone.utc)

    visitor_session.exit_time = now
    visitor_session.last_activity_at = now
    visitor_session.usage_seconds = max(
        0,
        int((now - visitor_session.entry_time).total_seconds()),
    )

    db.commit()
    db.refresh(visitor_session)

    return visitor_session