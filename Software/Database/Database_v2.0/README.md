# Database v2.0 — Base de datos oficial de la plataforma Ambisonics

Paquete de despliegue de la base de datos final de la plataforma web (`web site v3.0 FINAL`). Contiene el esquema SQL de referencia, los modelos SQLAlchemy y un script de inicialización independiente.

> Los routers y servicios del backend **no se duplican aquí**: viven en `Software/web site/web site v3.0 FINAL/backend/`. Esta carpeta solo documenta y empaqueta la capa de datos.

## Motor

**PostgreSQL Serverless en [Neon](https://neon.tech)** (base `neondb`, esquema `public`, servidor PostgreSQL 18.x). Se accede desde el backend FastAPI con SQLAlchemy y `psycopg2`, mediante la variable de entorno `DATABASE_URL`.

## Contenido

| Archivo | Descripción |
|---|---|
| `ambisonics_schema_v2.sql` | Esquema oficial (solo estructura, sin datos, sin dueños ni privilegios). Es la referencia para producción. |
| `models.py` | Modelos ORM (SQLAlchemy) de las 5 tablas. |
| `database.py` | Motor, sesión (`SessionLocal`), `Base` y dependencia `get_db()`. Lee `DATABASE_URL` desde `.env`. |
| `init_db.py` | Crea las tablas a partir de los modelos y lista lo creado. |
| `.env.example` | Plantilla de configuración con marcadores genéricos. |

## Tablas

| Tabla | Clave primaria | Claves foráneas | Descripción |
|---|---|---|---|
| `users` | `id` | — | Cuentas registradas: nombre, correo (único, sin distinguir mayúsculas), hash de contraseña, consentimiento y código de recuperación (hash). |
| `user_sessions` | `id` | `user_id → users.id` (`ON DELETE CASCADE`) | Sesiones autenticadas. Guarda el hash del token (único), actividad, expiración y revocación. |
| `processing_requests` | `id` | `user_id → users.id` (`ON DELETE SET NULL`) | Registro de cada conversión: archivo original, modo de entrada (`stereo`, `tetra_4mic`), estado (`processing`, `completed`, `failed`), frecuencias de muestreo, duraciones y errores. `user_id` puede ser nulo (uso sin cuenta). |
| `temporary_files` | `id` | `processing_request_id → processing_requests.id` (`ON DELETE CASCADE`) | Referencia a archivos temporales con fecha de expiración (24 h por defecto) y marca de borrado. |
| `suggestions` | `id` | — | Sugerencias de usuarios; nombre y correo opcionales, solo se guardan con consentimiento. |

```text
users 1 ──< user_sessions
users 1 ──< processing_requests 1 ──< temporary_files
suggestions  (independiente)
```

### Audio fuera de la base de datos

PostgreSQL **no almacena audio**. Los archivos WAV y los resultados viven en disco como archivos temporales del backend; la base solo guarda metadatos y la ruta (`temporary_files.storage_path`). Al vencer `expires_at`, el servicio de limpieza elimina el archivo y registra `deleted_at`, de modo que la base conserva únicamente el historial de solicitudes.

## Inicialización rápida

1. Crear el archivo de configuración a partir de la plantilla y completar la cadena de conexión real (el `.env` no se versiona):

   ```powershell
   Copy-Item .env.example .env
   ```

   ```env
   DATABASE_URL=postgresql://USUARIO:CONTRASENA@HOST/neondb?sslmode=require
   ```

2. Elegir **una** de las dos opciones:

   **Opción A — SQL (recomendada, esquema exacto):**

   ```bash
   psql "$DATABASE_URL" -f ambisonics_schema_v2.sql
   ```

   **Opción B — Python (crea las tablas desde los modelos ORM):**

   ```bash
   pip install sqlalchemy psycopg2-binary python-dotenv
   python init_db.py
   ```

`init_db.py` usa `database.py` y `models.py` de esta misma carpeta y no requiere el directorio `backend/`. Si las tablas ya existen, no las modifica.

> **Nota:** `ambisonics_schema_v2.sql` es la definición de referencia. Las tablas creadas con `init_db.py` pueden diferir en detalles menores (por ejemplo, algunas restricciones `CHECK` o el índice único sobre `lower(email)`), por lo que para producción se recomienda la Opción A.

## Seguridad

- No escribir credenciales reales en el repositorio: ni en `.env.example`, ni en este README, ni en scripts.
- El archivo `.env` real debe permanecer solo en la máquina o el servicio de despliegue.
- La cadena de conexión se mantiene exclusivamente en el backend; el frontend nunca la recibe.

## Versiones anteriores

El esquema previo (sesiones de visitante, `audio_files`, `conversion_jobs`) se conserva en `../Database_v1.0/`.