# routers/suggestions.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import Suggestion, VisitorSession
from schemas import SuggestionCreate, SuggestionOut


router = APIRouter(
    prefix="/suggestions",
    tags=["suggestions"],
)


@router.post(
    "",
    response_model=SuggestionOut,
    status_code=status.HTTP_201_CREATED,
)
def create_suggestion(
    suggestion_data: SuggestionCreate,
    db: Session = Depends(get_db),
):
    """
    Guarda una sugerencia y la relaciona con la sesión correspondiente.
    """

    # Buscar la sesión mediante el token enviado por la página.
    visitor_session = (
        db.query(VisitorSession)
        .filter(
            VisitorSession.session_token
            == suggestion_data.session_token
        )
        .first()
    )

    if visitor_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La sesión indicada no existe",
        )

    # Crear la sugerencia usando el id interno de la sesión.
    suggestion = Suggestion(
        session_id=visitor_session.id,
        name=suggestion_data.name.strip(),
        email=suggestion_data.email.strip().lower(),
        message=suggestion_data.message.strip(),
    )

    db.add(suggestion)
    db.commit()
    db.refresh(suggestion)

    return suggestion