import os
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Response, status, Cookie
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from backend.database import get_db
from backend.models import User, UserSession
from backend.schemas import UserCreate, UserLogin, UserResponse, PasswordChangeRequest, PasswordResetRequest, RegisterResponse, PasswordResetResponse, GenerateRecoveryCodeResponse
from backend.utils.security import hash_password, verify_password, generate_session_token, hash_token, generate_recovery_code
from backend.dependencies import get_current_user
import secrets

router = APIRouter(prefix="/api/auth", tags=["auth"])

SESSION_DURATION_DAYS = 7

def get_secure_cookie_config() -> bool:
    """Reads SECURE_COOKIES from env, defaults to false for local dev."""
    return os.getenv("SECURE_COOKIES", "false").lower() == "true"

@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=RegisterResponse)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    # consent_given ya está validado por Pydantic (debe ser True)
    
    hashed_password = hash_password(user_in.password)
    recovery_code = generate_recovery_code()
    recovery_code_hashed = hash_token(recovery_code)
    
    new_user = User(
        name=user_in.name,
        email=user_in.email,
        password_hash=hashed_password,
        recovery_code_hash=recovery_code_hashed,
        consent_given=True,
        consent_at=datetime.now(timezone.utc)
    )
    
    db.add(new_user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya está registrado."
        )
        
    return {"message": "Usuario registrado exitosamente", "recovery_code": recovery_code}

@router.post("/login")
def login(user_in: UserLogin, response: Response, db: Session = Depends(get_db)):
    # Buscar al usuario
    user = db.query(User).filter(User.email == user_in.email).first()
    
    # Prevenir enumeración: respuesta genérica
    if not user or not verify_password(user_in.password, user.password_hash) or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )
    
    # Crear sesión
    token = generate_session_token()
    token_hashed = hash_token(token)
    
    now = datetime.now(timezone.utc)
    expires = now + timedelta(days=SESSION_DURATION_DAYS)
    
    session_record = UserSession(
        user_id=user.id,
        token_hash=token_hashed,
        created_at=now,
        last_activity_at=now,
        expires_at=expires
    )
    db.add(session_record)
    db.commit()
    
    # Establecer cookie
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        samesite="lax",
        path="/",
        secure=get_secure_cookie_config(),
        max_age=SESSION_DURATION_DAYS * 24 * 60 * 60
    )
    
    return {"message": "Sesión iniciada exitosamente"}

@router.post("/logout")
def logout(
    response: Response,
    session_token: str = Cookie(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if session_token:
        hashed_token = hash_token(session_token)
        db_session = db.query(UserSession).filter(
            UserSession.token_hash == hashed_token,
            UserSession.user_id == current_user.id
        ).first()
        
        if db_session:
            db_session.revoked_at = datetime.now(timezone.utc)
            db.commit()
            
    response.delete_cookie(
        key="session_token",
        path="/",
        samesite="lax",
        secure=get_secure_cookie_config(),
        httponly=True
    )
    return {"message": "Sesión cerrada"}

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/change-password")
def change_password(
    req: PasswordChangeRequest, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    if not verify_password(req.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="La contraseña actual no es correcta.")
        
    current_user.password_hash = hash_password(req.new_password)
    
    # Revocar sesiones
    now = datetime.now(timezone.utc)
    for session in current_user.sessions:
        if session.revoked_at is None:
            session.revoked_at = now
            
    db.commit()
    return {"message": "Tu contraseña fue actualizada. Inicia sesión nuevamente."}

@router.post("/generate-recovery-code", response_model=GenerateRecoveryCodeResponse)
def generate_user_recovery_code(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_recovery_code = generate_recovery_code()
    current_user.recovery_code_hash = hash_token(new_recovery_code)
    db.commit()
    return {"message": "Código de recuperación generado exitosamente.", "recovery_code": new_recovery_code}

@router.post("/reset-password", response_model=PasswordResetResponse)
def reset_password(req: PasswordResetRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    
    if not user or not user.recovery_code_hash:
        raise HTTPException(status_code=400, detail="No fue posible verificar los datos de recuperación.")
        
    code_hash = hash_token(req.recovery_code)
    if not secrets.compare_digest(code_hash, user.recovery_code_hash):
        raise HTTPException(status_code=400, detail="No fue posible verificar los datos de recuperación.")
        
    # Todo bien, resetear
    user.password_hash = hash_password(req.new_password)
    
    new_recovery_code = generate_recovery_code()
    user.recovery_code_hash = hash_token(new_recovery_code)
    
    now = datetime.now(timezone.utc)
    for session in user.sessions:
        if session.revoked_at is None:
            session.revoked_at = now
            
    db.commit()
    return {"message": "Contraseña recuperada exitosamente.", "new_recovery_code": new_recovery_code}
