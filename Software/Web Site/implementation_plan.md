# Plan de Implementación - Conectar convert y demo, solucionar errores y añadir opción de Micrófono 2

Este plan detalla los pasos para solucionar los errores en la conversión de audio, habilitar el procesamiento del segundo modo (4 micrófonos tetraédricos) y conectar completamente los notebooks de Jupyter (`convert.ipynb` y `demo.ipynb`) al backend y frontend.

## User Review Required

> [!IMPORTANT]
> - **Cambios en `convert.ipynb`**: Se modificará el notebook para definir la función `normalize_multichannel` (que estaba ausente y causaba el error de ejecución) y se insertará la celda que ejecuta la conversión correspondiente según el modo seleccionado.
> - **Nuevo selector de modo en la UI**: Se añadirá un selector en la página principal para permitir al usuario elegir entre **Opción 1: Audio Estéreo** y **Opción 2: 4 Micrófonos (Tetraédrico)**.

## Proposed Changes

---

### Backend y Códigos (Python / Notebooks)

#### [MODIFY] [convert.ipynb](file:///c:/Users/Usuario/Downloads/ambisonic/Codigos/convert.ipynb) (vía script programático de actualización)
- **Celda de Parámetros (Celda 1)**: Añadir `mode = "auto"`.
- **Celda de Funciones (Celda 5)**: Agregar la definición de la función `normalize_multichannel` (copiada del notebook de demo):
  ```python
  def normalize_multichannel(audio: np.ndarray) -> np.ndarray:
      audio = audio.astype(np.float64)
      if audio.ndim == 1:
          audio = audio[:, None]
      audio = audio - np.mean(audio, axis=0, keepdims=True)
      peak = np.max(np.abs(audio)) + 1e-9
      return 0.95 * audio / peak
  ```
- **Celda de Selección de Modo (Celda 13)**: Actualizar para permitir que el backend le pase directamente el modo:
  ```python
  if use_external_input:
      if 'mode' in globals() and mode in ["stereo", "tetra_4mic"]:
          print(f"Modo recibido de backend: {mode}")
      else:
          if num_ch >= 4:
              mode = "tetra_4mic"
          elif num_ch == 2:
              mode = "stereo"
          else:
              raise ValueError("Se requiere un archivo estéreo (2 canales) o tetra (4 canales).")
      print(f"\nModo final usado automáticamente: {mode}")
  ```
- **Nueva Celda de Ejecución (después de Celda 13)**: Insertar una celda que invoque a las funciones de conversión de audio (que antes no se llamaban nunca):
  ```python
  # =========================================================
  # EJECUTAR CONVERSIÓN SEGÚN EL MODO
  # =========================================================
  if mode == "stereo":
      W, X, Y, Z, diagnostics = stereo_to_foa(audio, sr)
  elif mode == "tetra_4mic":
      W, X, Y, Z, diagnostics = tetra_aformat_to_foa(audio)
  else:
      raise ValueError(f"Modo no reconocido: {mode}")
  ```

#### [MODIFY] [main.py](file:///c:/Users/Usuario/Downloads/ambisonic/backend/main.py)
- Modificar el endpoint `/api/convert` para recibir `mode: str = Form("auto")` del frontend.
- Pasar este parámetro `mode` al ejecutar `convert.ipynb` mediante `papermill`.

---

### Frontend (Next.js)

#### [MODIFY] [api.ts](file:///c:/Users/Usuario/Downloads/ambisonic/lib/api.ts)
- Actualizar `convertAudio` para aceptar un parámetro `mode` (`'stereo' | 'tetra_4mic'`) y pasarlo al FormData en la petición POST.
- Mejorar el manejo de errores para extraer e informar el mensaje específico (`detail`) devuelto por FastAPI si ocurre un fallo.

#### [MODIFY] [conversor-client.tsx](file:///c:/Users/Usuario/Downloads/ambisonic/components/conversor/conversor-client.tsx)
- Añadir un estado local `conversionMode` para controlar la opción seleccionada.
- Diseñar y renderizar un selector visual premium tipo tarjetas/toggles para elegir entre la **Opción 1: Audio Estéreo** y la **Opción 2: 4 Micrófonos (Tetraédrico)**.
- Pasar `conversionMode` a la llamada a la función `convertAudio` al presionar "Procesar audio".
- Modificar el subtítulo/descripción para indicar que se soportan archivos estéreo o de 4 canales.

## Verification Plan

### Automated Tests
- Ejecutar el servidor backend FastAPI localmente:
  ```powershell
  .venv\Scripts\uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
  ```
- Ejecutar el script `verify.py` para asegurar que las rutas `/api/health`, `/api/convert` (con el notebook modificado) y `/api/demo` funcionan sin lanzar errores.
  ```powershell
  python backend/verify.py
  ```

### Manual Verification
- Levantar el frontend local con `pnpm dev` (o `npm run dev`).
- Probar la conversión subiendo un audio estéreo con la Opción 1.
- Probar la conversión subiendo un audio de 4 canales con la Opción 2 (o verificar que arroje error explicativo si se sube un audio incorrecto).
- Probar el apartado de Demo para validar que sigue funcionando correctamente con sus parámetros de posicionamiento.
