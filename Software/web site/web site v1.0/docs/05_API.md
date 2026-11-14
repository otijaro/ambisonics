# 05. Referencia de la API

La API del proyecto está expuesta por el servidor de FastAPI en el backend (`backend/main.py`). Se encarga de procesar los archivos de audio subidos por el cliente (vía `FormData` Multipart) y devolver las URLs relativas donde el audio procesado queda alojado temporalmente.

## Rutas Principales

---

### `GET /api/health`
**Propósito:** Verificar el estado del servidor. Usado por servicios de monitoreo o infraestructura de despliegue para comprobar que la API levantó correctamente.
- **Request:** (Ninguno)
- **Response:**
  ```json
  { "status": "healthy" }
  ```

---

### `POST /api/convert`
**Propósito:** Endpoint principal del "Conversor". Toma un audio completo, determina su duración y dispara el motor OLA de streaming o de memoria.
- **Parámetros (FormData):**
  - `audio`: (File, requerido) El archivo a convertir (típicamente `.wav` o `.mp3`).
  - `mode`: (String, requerido) Modalidad de conversión. Puede ser `"auto"`, `"stereo"`, o `"tetra_4mic"`.
- **Flujo:** Genera un UUID único, crea un directorio estático temporal en `/backend/static/{uuid}/`, guarda el archivo `input.wav` y ejecuta el procesamiento.
- **Posibles Errores:**
  - `500 Internal Server Error`: Si falla la decodificación del audio con `soundfile` o hay un fallo matemático.
- **Response (Ejemplo exitoso):**
  ```json
  {
      "outputs": [
          {
              "key": "binaural",
              "wavUrl": "/static/a1b2-c3d4/output_binaural.wav",
              "mp3Url": "/static/a1b2-c3d4/output_binaural.mp3"
          },
          {
              "key": "binaural_3d",
              "wavUrl": "/static/a1b2-c3d4/output_binaural_3D_perceptual.wav",
              "mp3Url": "/static/a1b2-c3d4/output_binaural_3D_perceptual.mp3"
          }
      ],
      "processingTime": 12.35,
      "audioDuration": 210.4,
      "processingRatio": 5.86,
      "outputsCount": 6
  }
  ```

---

### `POST /api/demo`
**Propósito:** Endpoint para la Demo Interactiva. A diferencia de `/convert`, este ruta trunca el audio a máximo 15 segundos y aplica variables de deformación espacial dinámicas basándose en los sliders de la interfaz.
- **Parámetros (FormData):**
  - `audio`: (File) Archivo de audio estéreo (preferiblemente de corta duración).
  - `direccion`: (Float) Shift azimutal de -180 a 180.
  - `altura`: (Float) Porcentaje de 0 a 100 indicando el refuerzo en el eje Z.
  - `apertura`: (Float) Porcentaje indicando qué tan estéreo/difuso es el sonido.
  - `movimiento`: (Float) Porcentaje para la órbita animada automática.
- **Response:**
  ```json
  {
      "binaural": {
          "wavUrl": "/static/x9y8-z7w6/preview_binaural.wav",
          "mp3Url": "/static/x9y8-z7w6/preview_binaural.mp3"
      },
      "binaural_3d": {
          "wavUrl": "/static/x9y8-z7w6/preview_3d_perceptual.wav",
          "mp3Url": "/static/x9y8-z7w6/preview_3d_perceptual.mp3"
      }
  }
  ```

---

### `POST /api/feedback`
**Propósito:** Recibir formularios de contacto/sugerencias desde el frontend. No usa base de datos, apendiza el objeto JSON al archivo local `backend/feedback.json`.
- **Parámetros (JSON Payload):**
  - `nombre` (string)
  - `correo` (string)
  - `mensaje` (string)
- **Response:**
  ```json
  { "status": "ok" }
  ```
