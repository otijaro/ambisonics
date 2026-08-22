# 03. Backend

El backend de **Ambisonic** está construido en Python y utiliza **FastAPI** como framework principal debido a su alto rendimiento, soporte asíncrono y generación automática de documentación. No existe una base de datos relacional; los archivos generados se sirven de manera estática y efímera desde un directorio local temporal (`backend/static`).

## Tecnologías del Backend
- **Framework:** FastAPI (Uvicorn como servidor ASGI)
- **Procesamiento Asíncrono:** Uso de `async def` para recepción de archivos (I/O).
- **Procesamiento Síncrono (CPU bound):** El procesamiento DSP corre de forma nativa bloqueando el hilo, pero de manera altamente optimizada por NumPy.
- **Audio I/O:** `soundfile`
- **Conversión Final:** `ffmpeg` mediante `subprocess` (Llamado al sistema operativo para MP3).

## Descripción de Archivos Clave

### `backend/main.py`
**Propósito:** Es el punto de entrada de la aplicación API. Se encarga de instanciar FastAPI, montar el middleware CORS, gestionar el ciclo de vida (cargar HRTF en memoria al inicio) y exponer los endpoints.
- **Funciones Principales:**
    - `lifespan(app: FastAPI)`: Carga el archivo `hrtf.sofa` en un estado global (RAM) durante el arranque para evitar leer 3MB del disco en cada petición.
    - `health_check()`: Endpoint básico de monitoreo (`GET /api/health`).
    - `convert_audio()`: Recibe la petición del *Conversor*, guarda el `input.wav` temporal y orquesta la llamada a `native_convert_audio`.
    - `run_demo_notebook()`: Similar a convert, pero extrae los metadatos de los sliders del frontend y llama a `native_process_demo`.
    - `save_feedback()`: Endpoint para guardar un JSON estático (`feedback.json`) con comentarios de los usuarios.
- **Dependencias:** `fastapi`, `soundfile`, `uuid`, `backend.processor`.

### `backend/processor.py`
**Propósito:** Intermediario entre la capa web (API) y el corazón matemático (DSP). Se encarga del ruteo, el guardado físico de los archivos y la optimización del procesamiento (Streaming OLA vs En Memoria).
- **Funciones Principales:**
    - `convert_audio(input_path, output_dir, mode, hrtf, pos)`: Evalúa la duración del audio. Si es corto (<60s) procesa todo en memoria. Si es largo, hace procesamiento por streaming usando `sf.blocks`. Al finalizar, exporta a WAV y dispara asíncronamente FFmpeg para MP3.
    - `process_demo(...)`: Recorta el audio a máximo 15 segundos y mapea los parámetros de la UI (Dirección, Altura, Apertura, Movimiento) utilizando `build_demo_params` antes de enviarlos a `core_dsp.py`.
- **Dependencias:** `numpy`, `soundfile`, `subprocess`, `backend.core_dsp`.

### `backend/core_dsp.py`
**Propósito:** (Explicado detalladamente en [04. DSP](04_DSP.md)). Contiene todas las funciones matemáticas de procesamientos espaciales. Aquí NO hay dependencias web ni de guardado de disco.
- **Funciones Principales:** `stereo_to_foa`, `foa_to_binaural`, `tetra_aformat_to_foa`, etc.

### `backend/verify.py`
**Propósito:** Script interno de diagnóstico para verificar que las funciones núcleo de DSP operan correctamente y que se encuentran las librerías instaladas en el entorno local (usado en etapas previas de desarrollo, no atado a la API principal).

## Flujo Completo de la Aplicación

```mermaid
flowchart TD
    A[Frontend: Usuario sube 'cancion.mp3'] --> B(lib/api.ts)
    B -- "POST /api/convert (Multipart)" --> C[backend/main.py]
    C --> D{Crea ID de sesión única (UUID)}
    D --> E[Guarda 'input.wav' en static/]
    E --> F[processor.py: convert_audio]
    F --> G{¿Es mayor a 60 segundos?}
    G -- Sí --> H[Procesamiento por bloques (Streaming OLA)]
    G -- No --> I[Procesamiento en Memoria]
    H --> J[core_dsp.py: Operaciones Vectoriales]
    I --> J
    J --> K[Escribe WAV en static/]
    K --> L[Lanza subprocess 'ffmpeg' a MP3]
    L --> M[Retorna JSON con rutas relativas a main.py]
    M --> N[Frontend recibe URLs]
    N --> O[Componente audio-result.tsx renderiza reproductores]
```
