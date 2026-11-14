import os
from datetime import datetime, timezone
import traceback
from sqlalchemy.orm import Session
from backend.database import get_db, SessionLocal
from backend.models import TemporaryFile

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOG_FILE = os.path.join(BASE_DIR, "cleanup.log")

def log_cleanup_result(found, physically_deleted, already_missing, errors, error_messages):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] Ejecución de limpieza\n")
        f.write(f"  - Vencidos encontrados: {found}\n")
        f.write(f"  - Eliminados físicamente: {physically_deleted}\n")
        f.write(f"  - Ya no existían: {already_missing}\n")
        f.write(f"  - Errores de eliminación: {errors}\n")
        for err in error_messages:
            f.write(f"    * Error: {err}\n")
        f.write("-" * 50 + "\n")

def cleanup_expired_files(db: Session = None):
    """
    Busca archivos temporales expirados que no han sido eliminados,
    los elimina físicamente del disco y actualiza deleted_at en la DB.
    """
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True

    try:
        now = datetime.now(timezone.utc)
        expired_files = db.query(TemporaryFile).filter(
            TemporaryFile.expires_at <= now,
            TemporaryFile.deleted_at.is_(None)
        ).all()

        found = len(expired_files)
        physically_deleted = 0
        already_missing = 0
        errors = 0
        error_messages = []

        for temp_file in expired_files:
            file_deleted = False

            if not os.path.exists(temp_file.storage_path):
                # Si el archivo ya no existe, lo consideramos eliminado
                file_deleted = True
                already_missing += 1
            else:
                try:
                    os.remove(temp_file.storage_path)
                    file_deleted = True
                    physically_deleted += 1
                except Exception as e:
                    errors += 1
                    err_msg = str(e)
                    print(f"Error al eliminar el archivo físico {temp_file.storage_path}: {err_msg}")
                    error_messages.append(err_msg)
                    # No actualizamos deleted_at para intentar de nuevo más tarde
            
            if file_deleted:
                temp_file.deleted_at = datetime.now(timezone.utc)

        if expired_files:
            db.commit()

        log_cleanup_result(found, physically_deleted, already_missing, errors, error_messages)
        return found, physically_deleted, errors
    finally:
        if close_db:
            db.close()

if __name__ == "__main__":
    found, physically_deleted, errors = cleanup_expired_files()
    print(f"Archivos vencidos encontrados: {found}")
    print(f"eliminados: {physically_deleted}")
    print(f"errores: {errors}")
