import os
from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.database import get_db
from backend import models
from backend import schemas
from backend.dependencies import get_optional_user, get_current_user


router = APIRouter(
    prefix="/api/processing-requests",
    tags=["Processing Requests"],
)

@router.post("", response_model=schemas.ProcessingRequest, status_code=status.HTTP_201_CREATED)
def create_processing_request(
    request_in: schemas.ProcessingRequestCreate,
    db: Session = Depends(get_db),
    user: models.User | None = Depends(get_optional_user)
):
    db_request = models.ProcessingRequest(
        **request_in.model_dump(),
        status="processing",
        user_id=user.id if user else None
    )
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request

@router.get("/mine", response_model=List[schemas.ProcessingRequestMineResponse])
def get_my_processing_requests(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    requests = db.query(models.ProcessingRequest).filter(
        models.ProcessingRequest.user_id == current_user.id
    ).order_by(models.ProcessingRequest.requested_at.desc()).all()

    response = []
    now = datetime.now(timezone.utc)
    for req in requests:
        file_status = "deleted"
        is_available = False
        
        # Obtenemos todos los archivos asociados a la solicitud
        db_files = db.query(models.TemporaryFile).filter(
            models.TemporaryFile.processing_request_id == req.id
        ).all()
        
        # Para simplificar el status global, revisamos el primero (o "input" si existe)
        if db_files:
            first_file = db_files[0]
            if first_file.deleted_at:
                file_status = "deleted"
            elif first_file.expires_at <= now:
                file_status = "expired"
            else:
                file_status = "available"
                is_available = True
                
        # Proyectar solo el file_type para evitar exponer storage_path
        files_list = [{"file_type": f.file_type} for f in db_files if f.file_type != "input"]
        
        resp_dict = req.__dict__.copy()
        resp_dict["file_status"] = file_status
        resp_dict["is_available"] = is_available
        resp_dict["files"] = files_list
        # input_mode ya está en req.__dict__
        
        response.append(schemas.ProcessingRequestMineResponse(**resp_dict))
        
    return response

@router.patch("/{request_id}", response_model=schemas.ProcessingRequest)
def update_processing_request(
    request_id: int,
    request_in: schemas.ProcessingRequestUpdate,
    db: Session = Depends(get_db)
):
    db_request = db.query(models.ProcessingRequest).filter(models.ProcessingRequest.id == request_id).first()
    if not db_request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Processing request not found")

    update_data = request_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_request, key, value)

    db.commit()
    db.refresh(db_request)
    return db_request

ALLOWED_FILE_TYPES = {"binaural", "binaural_mp3", "binaural_3d", "binaural_3d_mp3"}
OUTPUTS_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static"))

@router.get("/{request_id}/file/{file_type}")
def download_processing_request_file(
    request_id: int,
    file_type: str,
    download: bool = False,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if file_type not in ALLOWED_FILE_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File type not allowed")

    db_request = db.query(models.ProcessingRequest).filter(
        models.ProcessingRequest.id == request_id,
        models.ProcessingRequest.user_id == current_user.id
    ).first()

    if not db_request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Processing request not found")

    db_file = db.query(models.TemporaryFile).filter(
        models.TemporaryFile.processing_request_id == request_id,
        models.TemporaryFile.file_type == file_type
    ).first()

    if not db_file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    now = datetime.now(timezone.utc)
    if db_file.deleted_at or db_file.expires_at <= now:
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="File has expired or has been deleted")

    try:
        abs_storage_path = os.path.abspath(db_file.storage_path)
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Invalid path")

    if not abs_storage_path.startswith(OUTPUTS_BASE_DIR):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    if not os.path.exists(abs_storage_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Physical file not found on server")
    
    media_type = "audio/mpeg" if file_type.endswith("_mp3") else "audio/wav"
    ext = ".mp3" if file_type.endswith("_mp3") else ".wav"
    
    safe_orig = "".join([c for c in db_request.original_filename if c.isalnum() or c in (' ', '-', '_')]).strip()
    if not safe_orig:
        safe_orig = "audio"
        
    download_filename = f"{safe_orig}_{file_type}{ext}"
    
    headers = {}
    if not download:
        headers["Content-Disposition"] = f'inline; filename="{download_filename}"'

    return FileResponse(
        path=abs_storage_path, 
        media_type=media_type, 
        filename=download_filename if download else None,
        headers=headers if not download else None
    )
