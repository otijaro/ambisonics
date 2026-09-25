from datetime import datetime, timezone
from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import UserSession, User
from backend.utils.security import hash_token

def get_current_user(
    session_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the currently authenticated user from the session cookie.
    Validates the token, checks expiration and revocation, and returns the User.
    Updates last_activity_at on successful validation.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No autenticado",
    )
    
    if not session_token:
        raise credentials_exception
        
    hashed_token = hash_token(session_token)
    
    # Buscar sesión activa
    db_session = db.query(UserSession).filter(
        UserSession.token_hash == hashed_token,
        UserSession.revoked_at.is_(None),
        UserSession.expires_at > datetime.now(timezone.utc)
    ).first()
    
    if not db_session:
        raise credentials_exception
        
    user = db_session.user
    if not user or not user.is_active:
        raise credentials_exception
        
    now_utc = datetime.now(timezone.utc)
    
    # Check inactividad (15 minutos)
    from datetime import timedelta
    if (now_utc - db_session.last_activity_at) >= timedelta(minutes=15):
        db_session.revoked_at = now_utc
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión expirada por inactividad"
        )
        
    # Actualizar última actividad
    db_session.last_activity_at = now_utc
    db.commit()
    
    return user

def get_optional_user(
    session_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db)
) -> User | None:
    """
    Dependency to get the currently authenticated user from the session cookie if it exists.
    Returns None if there is no session or it is invalid.
    """
    if not session_token:
        return None
        
    hashed_token = hash_token(session_token)
    
    # Buscar sesión activa
    db_session = db.query(UserSession).filter(
        UserSession.token_hash == hashed_token,
        UserSession.revoked_at.is_(None),
        UserSession.expires_at > datetime.now(timezone.utc)
    ).first()
    
    if not db_session:
        return None
        
    user = db_session.user
    if not user or not user.is_active:
        return None
        
    now_utc = datetime.now(timezone.utc)
    
    # Check inactividad (15 minutos)
    from datetime import timedelta
    if (now_utc - db_session.last_activity_at) >= timedelta(minutes=15):
        db_session.revoked_at = now_utc
        db.commit()
        return None
        
    # Actualizar última actividad
    db_session.last_activity_at = now_utc
    db.commit()
    
    return user

