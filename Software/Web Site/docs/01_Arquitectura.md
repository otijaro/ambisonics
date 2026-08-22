# 01. Arquitectura del Proyecto

El proyecto está organizado en una estructura híbrida de mono-repositorio que agrupa el código del Frontend (Next.js) y del Backend (FastAPI). A continuación, se detalla el árbol principal del proyecto y el propósito de cada directorio importante.

## Estructura Principal

```text
ambisonic/
├── app/                  # Frontend: Rutas y páginas de Next.js (App Router)
├── backend/              # Backend: API en FastAPI y motor DSP en Python
├── components/           # Frontend: Componentes reutilizables de React (UI y 3D)
├── docs/                 # Documentación técnica del proyecto (Markdown)
├── lib/                  # Frontend: Utilidades y funciones de red (API client)
├── public/               # Frontend: Archivos estáticos (imágenes, video, fonts)
├── .env.local            # Variables de entorno locales
├── package.json          # Dependencias y scripts de Node.js (Frontend)
├── requirements.txt      # Dependencias de Python (Backend)
└── hrtf.sofa             # Archivo esencial de datos HRTF para convolución binaural
```

## Descripción Detallada de Carpetas

### `app/`
*   **Para qué sirve:** Define las rutas y la estructura de navegación del sitio web según el modelo *App Router* de Next.js.
*   **Qué contiene:** Archivos `page.tsx` (contenido de la ruta), `layout.tsx` (envoltorios persistentes) y `globals.css` (hoja de estilos global Tailwind). Subcarpetas como `demo/`, `conversor/`, `guia/`, `acerca-de/` y `sugerencias/`.
*   **Quién la utiliza:** Next.js la usa para construir el frontend y rutear las URLs del navegador.

### `backend/`
*   **Para qué sirve:** Aloja la lógica del servidor API de la plataforma y el motor de procesamiento de audio profundo.
*   **Qué contiene:** 
    *   `main.py`: Configuración de FastAPI y definición de endpoints.
    *   `processor.py`: Lógica intermedia que orquesta la lectura, procesamiento y guardado asíncrono.
    *   `core_dsp.py`: Corazón matemático del proyecto (Procesamiento Digital de Señales, matrices Ambisonics, filtros HRTF).
    *   `static/`: Directorio autogenerado en tiempo de ejecución para guardar temporalmente audios creados.
*   **Quién la utiliza:** Peticiones HTTP originadas en el frontend (`lib/api.ts`).

### `components/`
*   **Para qué sirve:** Almacena piezas de interfaz gráfica independientes, reutilizables y atómicas para mantener la limpieza del directorio `app/`.
*   **Qué contiene:** 
    *   `demo/`: Componentes específicos de interactividad y Canvas 3D (`visualizer-3d.tsx`).
    *   `conversor/`: Lógica de formularios y *dropzone* para subir audios.
    *   `ui/`: Componentes base (Botones, Sliders, Cards) generalmente exportados por librerías como *shadcn/ui*.
*   **Quién la utiliza:** Las páginas dentro de `app/` para construir la vista final.

### `lib/`
*   **Para qué sirve:** Aloja código lógico, puro (no visual) para el frontend.
*   **Qué contiene:** Principalmente `api.ts` (funciones wrapper para usar `fetch` hacia el backend) y `utils.ts` (funciones utilitarias como concatenación de clases Tailwind usando `clsx` y `tailwind-merge`).
*   **Quién la utiliza:** Los componentes de React y páginas que requieran comunicarse con FastAPI o formatear datos.

### `public/`
*   **Para qué sirve:** Sirve recursos estáticos públicos para el frontend sin pasar por Webpack/Turbopack.
*   **Qué contiene:** Archivos `.mp4` (videos de la guía o landing), imágenes `.jpeg`/`.png` e iconos.
*   **Quién la utiliza:** Componentes y páginas a través de rutas absolutas como `<img src="/imagenmuestra.jpeg" />`.

### Hallazgos y Observaciones
*Se han detectado varias carpetas y archivos huérfanos que corresponden a copias de seguridad de versiones anteriores o scripts de pruebas experimentales. Ejemplos: `Codigos/`, `backup_antes_de_3d_app/`, `out_blocks/`, `test_audio.wav`, `main_bak.py`. Estos no se utilizan en la versión de producción actual.*
