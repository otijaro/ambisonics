# Backend de la plataforma Ambisonics

Backend desarrollado con **FastAPI**, **SQLAlchemy** y **PostgreSQL** para soportar el subsistema de registro de solicitudes de procesamiento de audio de la plataforma web Ambisonics.

La base de datos PostgreSQL del proyecto se encuentra actualmente desplegada en **Neon**, permitiendo que los registros permanezcan disponibles en la nube sin depender de una instancia PostgreSQL ejecutándose en un computador local.

El backend registra sesiones de visitantes, metadatos de los archivos recibidos, solicitudes de conversión, estados de procesamiento, métricas y sugerencias de los usuarios.

> **Importante:** PostgreSQL no almacena el contenido binario de los archivos WAV/MP3. Los audios utilizados por el backend son archivos de trabajo temporales. La base de datos conserva únicamente los registros y metadatos necesarios.

---

## 1. Arquitectura actual

```text
Frontend web
      ↓
Backend FastAPI
      ↓
SQLAlchemy + psycopg2
      ↓
PostgreSQL en Neon
```

Actualmente FastAPI puede ejecutarse localmente y conectarse directamente con la base PostgreSQL alojada en Neon.

El despliegue público del backend será una etapa posterior.

---

## 2. Estructura principal

```text
ambisonics_backend/
├── migrations/
│   ├── 001_extend_conversion_jobs.sql
│   └── 002_add_session_to_audio_files.sql
│
├── routers/
│   ├── __init__.py
│   ├── audios.py
│   ├── conversions.py
│   ├── sessions.py
│   └── suggestions.py
│
├── services/
│   ├── __init__.py
│   └── conversion_service.py
│
├── .env.example
├── .gitignore
├── ambisonics_schema.sql
├── database.py
├── main.py
├── models.py
├── README.md
├── requirements.txt
└── schemas.py
```

Las carpetas `uploads/` y `outputs/` pueden generarse durante la ejecución para manejar archivos temporales.

No deben incluirse audios reales ni resultados de prueba dentro de la entrega del código.

---

## 3. Requisitos

* Python compatible con las dependencias del proyecto.
* Conexión a Internet para acceder a PostgreSQL en Neon.
* PowerShell, CMD o una terminal equivalente.
* Acceso al proyecto de Neon para los integrantes que necesiten ejecutar o administrar el backend.

No es necesario instalar PostgreSQL localmente para utilizar la base de datos remota de Neon.

---

## 4. Crear el entorno virtual

Desde la carpeta raíz del backend:

```powershell
python -m venv venv
```

Activarlo en PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

Cuando esté correctamente activado aparecerá:

```text
(venv)
```

al comienzo de la terminal.

---

## 5. Instalar las dependencias

Con el entorno virtual activo:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

La carpeta `venv/` no se comparte. Cada integrante crea su propio entorno utilizando `requirements.txt`.

---

## 6. Configuración de variables de entorno

El proyecto utiliza un archivo privado:

```text
.env
```

Este archivo **no debe incluirse en GitHub, ZIP de entrega, correo, Drive ni ningún otro medio de distribución**.

Cada desarrollador debe crear su propio `.env`.

La plantilla pública se encuentra en:

```text
.env.example
```

Ejemplo:

```env
DATABASE_URL=postgresql+psycopg2://USUARIO:CONTRASENA@HOST-POOLER/neondb?sslmode=require

FRONTEND_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173
```

Para obtener la conexión real:

```text
Neon
→ proyecto ambisonics-platform
→ Connect
→ Connection pooling activado
→ Connection string
```

La cadena entregada por Neon normalmente comienza con:

```text
postgresql://
```

Para este backend se utiliza el dialecto de SQLAlchemy con `psycopg2`, por lo que debe quedar:

```text
postgresql+psycopg2://
```

Ejemplo estructural:

```env
DATABASE_URL=postgresql+psycopg2://USUARIO:CONTRASENA@HOST-POOLER/neondb?sslmode=require
```

Nunca colocar credenciales reales en `.env.example`.

---

## 7. Base de datos PostgreSQL en Neon

La base actualmente utilizada es:

```text
neondb
```

El esquema contiene las tablas:

```text
users
visitor_sessions
audio_files
conversion_jobs
suggestions
```

La base desplegada en Neon ya contiene el esquema consolidado del proyecto.

### Instalación nueva de la base

Para crear una base desde cero se utiliza:

```text
ambisonics_schema.sql
```

Este archivo incluye la estructura consolidada y los cambios previamente introducidos mediante:

```text
migrations/001_extend_conversion_jobs.sql
migrations/002_add_session_to_audio_files.sql
```

Las migraciones se conservan como trazabilidad histórica del desarrollo.

No deben ejecutarse nuevamente sobre la instancia actual de Neon, ya que sus cambios ya están incluidos.

---

## 8. Comprobar la conexión con Neon

Con el entorno virtual activo:

```powershell
python -c "from database import engine; from sqlalchemy import text; conn=engine.connect(); print('HOST:', engine.url.host); print('DB/USER:', conn.execute(text('SELECT current_database(), current_user')).fetchone()); conn.close()"
```

Una conexión correcta debe indicar un host de Neon, por ejemplo:

```text
HOST: ...-pooler....neon.tech
DB/USER: ('neondb', 'neondb_owner')
```

---

## 9. Ejecutar FastAPI

Con el entorno virtual activo:

```powershell
uvicorn main:app --reload
```

Direcciones locales:

```text
API:      http://127.0.0.1:8000
Swagger:  http://127.0.0.1:8000/docs
ReDoc:    http://127.0.0.1:8000/redoc
```

Swagger permite probar los endpoints mientras se realiza el desarrollo e integración.

---

## 10. Flujo actual del visitante

### Crear una sesión

```http
POST /sessions/start
```

El backend genera un `session_token` único.

Ejemplo conceptual:

```json
{
  "id": 1,
  "session_token": "UUID_GENERADO"
}
```

El frontend conserva temporalmente este token y lo utiliza para identificar las solicitudes pertenecientes a la misma sesión.

---

### Subir un audio

```http
POST /upload
Content-Type: multipart/form-data
```

Campos:

```text
session_token
file
```

El backend valida que la sesión exista y registra los metadatos del archivo en:

```text
audio_files
```

Para visitantes:

```text
user_id = NULL
session_id = ID de la sesión correspondiente
```

---

### Solicitar una conversión

```http
POST /convert
Content-Type: application/json
```

Ejemplo:

```json
{
  "audio_file_id": 1,
  "session_token": "UUID_DE_LA_SESION",
  "ambisonics_format": "ACN_SN3D",
  "processing_mode": "memory"
}
```

El backend verifica que el archivo pertenezca a la misma sesión antes de crear el trabajo.

El registro se almacena en:

```text
conversion_jobs
```

---

### Consultar trabajos

```http
GET /jobs?session_token=UUID_DE_LA_SESION
```

Consultar un trabajo:

```http
GET /jobs/{job_id}?session_token=UUID_DE_LA_SESION
```

Descargar un resultado disponible:

```http
GET /jobs/{job_id}/download?session_token=UUID_DE_LA_SESION
```

---

### Consultar audios asociados

```http
GET /audios?session_token=UUID_DE_LA_SESION

GET /audios/{audio_id}?session_token=UUID_DE_LA_SESION

GET /audios/{audio_id}/download?session_token=UUID_DE_LA_SESION
```

El backend verifica siempre la asociación entre el recurso y la sesión.

---

### Actividad de sesión

```http
PATCH /sessions/{session_token}/activity
```

---

### Finalizar una sesión

```http
POST /sessions/{session_token}/end
```

Esto permite registrar información como tiempo de salida y duración de uso.

---

### Enviar una sugerencia

```http
POST /suggestions
```

Ejemplo:

```json
{
  "session_token": "UUID_DE_LA_SESION",
  "name": "Nombre",
  "email": "correo@ejemplo.com",
  "message": "Contenido de la sugerencia"
}
```

La sugerencia queda relacionada con la sesión correspondiente.

---

## 11. Protección de recursos por sesión

Actualmente las operaciones relacionadas con audios y conversiones validan el `session_token`.

Esto aplica a:

```text
POST /upload

GET /audios
GET /audios/{audio_id}
GET /audios/{audio_id}/download

POST /convert

GET /jobs
GET /jobs/{job_id}
GET /jobs/{job_id}/download
```

Conocer solamente un `audio_id` o un `job_id` no permite acceder al recurso si este no pertenece a la sesión indicada.

---

## 12. Almacenamiento de audio

PostgreSQL **no almacena los archivos de audio**.

La tabla `audio_files` contiene únicamente metadatos y referencias necesarias durante el procesamiento.

Entre la información registrada pueden encontrarse:

```text
original_filename
file_format
sample_rate
duration_seconds
session_id
uploaded_at
```

Los archivos utilizados durante la ejecución son considerados temporales.

El objetivo de persistencia del sistema es conservar principalmente:

```text
sesiones
solicitudes
estados
metadatos
métricas de procesamiento
sugerencias
```

y no mantener una biblioteca permanente de archivos de audio.

La automatización definitiva para eliminar archivos temporales forma parte de las tareas pendientes del backend.

---

## 13. Estado actual

Actualmente se encuentra implementado y probado:

```text
PostgreSQL desplegado en Neon
Conexión FastAPI → Neon
Sesiones de visitantes
Registro de metadatos de audio
Relación audio ↔ sesión
Solicitudes de conversión
Relación conversión ↔ sesión
Consulta de trabajos por sesión
Protección de recursos mediante session_token
Registro de sugerencias
Métricas adicionales en conversion_jobs
processing_mode
CORS configurable mediante variable de entorno
```

Las pruebas de integración realizadas confirmaron la creación de registros desde FastAPI directamente en PostgreSQL alojado en Neon.

---

## 14. Aspectos pendientes

Entre los siguientes pasos del proyecto se encuentran:

* Integrar el procesamiento DSP definitivo.
* Completar la generación de las métricas reales de procesamiento.
* Implementar la política automática de eliminación de archivos temporales.
* Publicar FastAPI en un servicio accesible desde Internet.
* Conectar el frontend desplegado con la URL pública del backend.
* Sustituir, si corresponde en la arquitectura final, el envío explícito del `session_token` por un mecanismo de sesión mediante cookie segura.
* Revisar la configuración de seguridad antes de la publicación definitiva.

---

## 15. Archivos que NO deben compartirse

```text
.env
venv/
__pycache__/
uploads/
outputs/
.pytest_cache/
.ruff_cache/
.mypy_cache/
*.log
```

Especialmente:

```text
.env
```

porque contiene la cadena privada de conexión a PostgreSQL.

---

## 16. Archivos que sí deben compartirse

```text
.env.example
.gitignore
requirements.txt
ambisonics_schema.sql
migrations/
routers/
services/
database.py
main.py
models.py
schemas.py
README.md
```

---

## 17. `.gitignore` recomendado

```gitignore
# Variables privadas
.env
.env.local
.env.*.local

# Entornos virtuales
venv/
.venv/

# Python
__pycache__/
*.py[cod]

# Archivos temporales de procesamiento
uploads/
outputs/

# Cachés
.pytest_cache/
.ruff_cache/
.mypy_cache/

# IDE
.vscode/
.idea/

# Sistema operativo
.DS_Store
Thumbs.db

# Logs
*.log
```

---

## 18. Configuración para otro integrante del proyecto

Después de recibir el código:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Después crear:

```text
.env
```

a partir de:

```text
.env.example
```

Los integrantes autorizados en Neon pueden acceder al proyecto y obtener desde el panel su cadena de conexión.

Finalmente:

```powershell
uvicorn main:app --reload
```

y abrir:

```text
http://127.0.0.1:8000/docs
```

para comprobar el funcionamiento de la API.

---

## 19. Seguridad

No publicar:

* contraseñas;
* cadenas `DATABASE_URL` reales;
* archivos `.env`;
* capturas donde sean visibles credenciales;
* archivos de audio privados utilizados en pruebas.

La conexión a PostgreSQL debe mantenerse exclusivamente en el backend mediante variables de entorno.

El frontend nunca debe contener directamente las credenciales de Neon.
