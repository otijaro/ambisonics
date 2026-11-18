#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
AMBISONIC — INICIALIZACIÓN Y MIGRACIÓN DE BASE DE DATOS POSTGRESQL
==============================================================================
Crea las 5 tablas oficiales (users, user_sessions, processing_requests,
temporary_files, suggestions) según los modelos SQLAlchemy en la base de datos configurada en .env.
==============================================================================
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from dotenv import load_dotenv
env_path = os.path.join(BASE_DIR, ".env")
load_dotenv(env_path)

def init_database():
    print("=" * 72)
    print("  AMBISONIC — INICIALIZACIÓN DE BASE DE DATOS POSTGRESQL")
    print("=" * 72)
    
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("\n❌ ERROR: No se encontró DATABASE_URL en el archivo .env.")
        print("Copia .env.example como .env y configura tu cadena de conexión PostgreSQL:")
        print("  DATABASE_URL=postgresql://USUARIO:CONTRASENA@HOST/neondb?sslmode=require\n")
        return False

    # Ocultar contraseña en el log de conexión
    safe_url = db_url
    if "@" in safe_url and ":" in safe_url:
        try:
            prefix, rest = safe_url.split("://", 1)
            user_pass, host_part = rest.split("@", 1)
            user = user_pass.split(":", 1)[0]
            safe_url = f"{prefix}://{user}:***@{host_part}"
        except Exception:
            safe_url = "postgresql://***:***@host/db"

    print(f"Conectando a: {safe_url}")

    try:
        from database import engine, Base
        import models  # noqa: F401  (registra las tablas en Base.metadata)

        print("Creando tablas e índices...")
        Base.metadata.create_all(bind=engine)

        print("\n✅ Tablas verificadas exitosamente:")
        for tbl in Base.metadata.sorted_tables:
            print(f"  • {tbl.name} ({len(tbl.columns)} columnas)")

        print("\nLa base de datos está lista para operar con usuarios y conversiones.")
        print("=" * 72)
        return True

    except Exception as e:
        print(f"\n❌ ERROR al conectar o crear las tablas: {e}")
        print("\nRecomendaciones:")
        print("  1. Verifica que el servicio de PostgreSQL esté en ejecución.")
        print("  2. Confirma que la base de datos indicada en DATABASE_URL ya exista.")
        print("  3. Comprueba usuario, contraseña, host y puerto en el archivo .env.")
        print("=" * 72)
        return False

if __name__ == "__main__":
    ok = init_database()
    sys.exit(0 if ok else 1)

