# Conversor Ambisonics v5.0 FINAL

Motor de conversión de audio a sonido ambisónico de primer orden (FOA, formato **AmbiX**: orden ACN, normalización SN3D) con decodificación binaural, en su versión final de producción. Los módulos de esta carpeta son una **copia fiel, sin modificaciones**, de los que ejecuta la plataforma web `Software/web site/web site v3.0 FINAL/`.

## 1. Por qué esta es la versión final

| Versión | Formato | Aporte (según el contenido de cada archivo) |
|---|---|---|
| v1.0 | Script `.py` | Primera conversión estéreo → FOA → binaural con una única HRTF (`hrtf.sofa`). |
| v2.0 | Notebook `.ipynb` | Incorpora el modo de arreglo tetraédrico de 4 micrófonos. |
| v3.0 | Notebook `.ipynb` | Incorpora `stabilize_loudness` (estabilización de sonoridad). |
| v4.0 | Notebook `.ipynb` | Versión consolidada del cuaderno; sigue usando una única HRTF. |
| **v5.0 FINAL** | Módulos Python | Arquitectura modular para servidor web (esta carpeta). |

Los cuadernos Jupyter sirvieron para explorar y validar el algoritmo, pero no son adecuados para producción: procesan el audio completo en memoria, mezclan experimentación y ejecución, y no atienden varias solicitudes a la vez. La versión v5.0 FINAL separa responsabilidades y añade:

- **Procesamiento por bloques con superposición y suma (Overlap-Add)** para audios largos, con memoria acotada.
- **Decodificador SAD** (*Sampling Ambisonic Decoder*) sobre una geometría octaédrica de 6 altavoces virtuales con pesos de cuadratura uniformes (1/6), en lugar del esquema empírico anterior.
- **HRIR SADIE II (sujeto D1) a 44,1, 48 y 96 kHz**, procesando a la frecuencia nativa de entrada, sin remuestreo.
- **Concurrencia controlada:** un semáforo asíncrono limita las conversiones simultáneas (`MAX_CONCURRENT_DSP`, 2 por defecto).
- **Objetivo de rendimiento:** factor de tiempo real $\text{RTF} < 0{,}60$, donde $\text{RTF} = T_{\text{proceso}} / T_{\text{audio}}$.

> **Medición orientativa.** En una prueba local con una señal estéreo sintética a 48 kHz (HRIR de 48 kHz, sin generación de MP3, un solo proceso) se obtuvo RTF ≈ 0,23 con 20 s de audio (modo en memoria) y RTF ≈ 0,34 con 70 s (modo por bloques). Es una verificación puntual de funcionamiento, no una medición formal: los resultados oficiales de rendimiento corresponden a los protocolos de validación (`Software/Validation/`).

## 2. Contenido y roles

```text
ambisonics_conversor_v5.0 FINAL/
├── main.py                  # Servicio FastAPI: punto de entrada y rutas de conversión
├── processor.py             # Pipeline de conversión y generación de salidas WAV/MP3
├── core_dsp.py              # Núcleo matemático DSP (AmbiX, SAD, binaural HRTF)
├── processing_requests.py   # Router puente de solicitudes de procesamiento y descarga
├── setup_sofa.py            # Verificación de las bases HRIR (tamaño y SHA-256)
├── requirements.txt         # Dependencias del motor DSP y servicio web
├── .gitignore               # Evita versionar los .sofa
└── sofa/
    └── .gitkeep             # Carpeta donde se instalan las bases HRIR (.sofa)
```

### `main.py`: servicio y punto de entrada
Recibe las solicitudes `POST /api/convert` (y la demo `POST /api/demo`), valida el archivo y los parámetros, y entrega las salidas con `GET /api/download/{session}/{archivo}`.
- Acepta dos modos de entrada: `stereo` (2 canales) y `tetra_4mic` (arreglo tetraédrico de 4 canales). Cualquier otro valor se trata como `stereo`.
- Valida la frecuencia de muestreo (solo 44,1, 48 y 96 kHz).
- Carga las bases SOFA en memoria al arrancar y las reutiliza.
- Ejecuta la conversión bajo el semáforo `dsp_semaphore`, que limita la concurrencia.
- Registra cada solicitud en la base de datos (`Software/Database/Database_v2.0/`).

### `processing_requests.py`: router puente de solicitudes y descargas
Actúa como puente entre las conversiones y la capa de persistencia/usuarios (`APIRouter` bajo `/api/processing-requests`):
- Crea y actualiza el estado de las solicitudes de procesamiento (`POST /api/processing-requests`, `PATCH /api/processing-requests/{request_id}`).
- Lista el historial de conversiones del usuario autenticado junto con la disponibilidad de sus archivos temporales (`GET /api/processing-requests/mine`).
- Gestiona la descarga segura por tipo de salida (`binaural`, `binaural_mp3`, `binaural_3d`, `binaural_3d_mp3`, `foa`) verificando sesión, vigencia y rutas dentro del almacenamiento temporal.

### Enrutamiento DSP por modo de entrada
No existe un `convert.py` separado en la versión web: la lógica de conversión del notebook se encuentra en `convert_audio()` de `processor.py`, que enruta según el parámetro `mode`:
- **Estéreo:** `stereo_to_foa()` estima la dirección de las fuentes y codifica a FOA.
- **Tetraédrico:** `tetra_aformat_to_foa()` convierte el formato A (4 cápsulas) a FOA con la matriz tetraédrica.

### `processor.py`: orquestación y salidas
`convert_audio(input_path, output_dir, mode, hrtf, pos)`:
- Para audios de **menos de 60 s** procesa en memoria; para audios más largos procesa por **bloques de 10 s** con Overlap-Add, conservando las colas de reverberación entre bloques.
- Genera tres salidas WAV (16 bits):
  - `output_foa.wav`: FOA AmbiX de 4 canales (orden W, Y, Z, X).
  - `output_binaural.wav`: decodificación binaural estándar.
  - `output_binaural_3D_perceptual.wav`: binaural con movimiento espacial perceptual, mezclado y estabilizado en sonoridad.
- Transcodifica a MP3 (320 kbps, `libmp3lame`) las dos salidas binaurales mediante `ffmpeg`, **solo si la frecuencia es ≤ 48 kHz** (MP3 no admite 96 kHz; en ese caso solo se entrega el WAV nativo).
- Devuelve la duración del audio, el tiempo total y la frecuencia usada.

### `core_dsp.py`: núcleo DSP
- Parámetros de la STFT: `N_FFT = 2048` y `HOP = 512`.
- **Codificación AmbiX ACN/SN3D** (`stereo_to_foa`, `tetra_aformat_to_foa`), con estimación direccional 3D basada en la STFT y la coherencia espectral local entre canales.
- **Decodificación virtual** a 6 altavoces (octaedro, `GEOMETRY_B_OCTAHEDRAL_SAD_SPEAKERS`) y **renderizado binaural** (`foa_to_binaural`) mediante convolución por Overlap-Add con HRIR, interpolando las 4 direcciones más cercanas (`get_hrtf_interp`). `foa_to_binaural_fallback` se usa si no hay HRIR disponible.
- `foa_motion_convert`: rotación continua del campo en acimut (0,12 vueltas/s) y oscilación en elevación (hasta ±60°) para la salida 3D perceptual.
- `stabilize_loudness`: control de ganancia por ventana (450 ms) usado en la salida 3D.
- `normalize_audio`, `validate_sample_rate` y la gestión de bases SOFA (`get_sadie_sofa_path`, `load_sofa`).

Este módulo contiene además geometrías y funciones de demostración (`*_demo`) usadas por la demo interactiva de la web.

### `sofa/`: bases HRIR (SADIE II D1)
Las respuestas impulsionales (HRIR, formato SOFA `SimpleFreeFieldHRIR`) permiten espacializar el audio en auriculares. El motor usa un archivo por frecuencia de muestreo:

| Frecuencia | Archivo | Tamaño |
|---|---|---|
| 44,1 kHz | `D1_44K_16bit_256tap_FIR_SOFA.sofa` | 36 310 650 bytes |
| 48 kHz | `D1_48K_24bit_256tap_FIR_SOFA.sofa` | 36 310 650 bytes |
| 96 kHz | `D1_96K_24bit_512tap_FIR_SOFA.sofa` | 72 366 402 bytes |

**Estos archivos no están en el repositorio** por su tamaño (35–69 MB cada uno); `.gitignore` impide subirlos por error.

## 3. Instalación de las bases HRIR

1. Descargar `D1_HRIR_SOFA.zip` de la base de datos SADIE II (University of York, licencia Apache 2.0):
   - Zenodo: https://zenodo.org/records/12092466/files/D1_HRIR_SOFA.zip?download=1
   - Proyecto: https://www.york.ac.uk/sadie-project/database.html
2. Extraer los tres archivos `.sofa` anteriores dentro de `sofa/` (o en `backend/sofa/` al desplegar dentro de `Software/web site/web site v3.0 FINAL/`).
3. Verificar tamaño e integridad (SHA-256):

   ```bash
   python setup_sofa.py
   ```

   El script indica qué archivos faltan o no coinciden y repite las instrucciones de descarga.

## 4. Requisitos y ejecución

- **Python** 3.10 a 3.12 (versión usada por la plataforma web).
- **ffmpeg** con `libmp3lame` en el `PATH` (solo para los MP3; sin él se omiten y se entregan los WAV).
- Dependencias: `pip install -r requirements.txt`

**Uso del motor.** `main.py` y `processing_requests.py` forman parte del servicio completo, cuyas dependencias internas (`backend.database`, `backend.models`, `backend.schemas`, `backend.dependencies`, `backend.routers.auth`, `backend.services.cleanup`, `backend.demo_processor`) residen en `Software/web site/web site v3.0 FINAL/backend/`. Para levantar la API web completa se ejecuta desde esa carpeta.

`processor.py` y `core_dsp.py` concentran el pipeline DSP y en el entorno web operan dentro del paquete `backend/`:

```python
from backend.core_dsp import load_sofa
from backend.processor import convert_audio

hrtf, pos = load_sofa("backend/sofa/D1_48K_24bit_256tap_FIR_SOFA.sofa")
duracion, tiempo_total, sr = convert_audio("entrada.wav", "salida/", "stereo", hrtf, pos)
```

La HRIR debe corresponder a la frecuencia de muestreo del audio de entrada.

## 5. Referencias

- Zotter, F. y Frank, M. (2019). *Ambisonics: A Practical 3D Audio Theory for Recording, Studio Production, Sound Reinforcement, and Virtual Reality*. Springer.
- Armstrong, C., Thresh, L., Murphy, D. y Kearney, G. (2018). A Perceptual Evaluation of Individual and Non-Individual HRTFs on Horizontal Localisation Accuracy. *Applied Sciences*, 8(11), 2029.
- SADIE II Spatial Audio Database, University of York AudioLab.