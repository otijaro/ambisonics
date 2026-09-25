# 07. Componentes (Frontend)

Este documento expone los componentes principales utilizados en la capa web (`components/`). Dado que el proyecto sigue la arquitectura de Next.js App Router, las páginas (`page.tsx`) son preferentemente "Server Components", por lo que los elementos interactivos se segregan y aíslan en esta carpeta para ejecutarse del lado del cliente (`'use client'`).

## Componentes de Interfaz Globales

### `navbar.tsx` y `footer.tsx`
- **Propósito:** Brindar navegación persistente.
- **Quién los utiliza:** Exclusivamente inyectados dentro de `app/layout.tsx` para persistir al cambiar de ruta.
- **Detalle:** Navbar contiene lógica reactiva condicional, determinando qué ruta es la actual (`usePathname()`) para pintar el enlace activo de color vibrante (violeta).

### `reveal.tsx`
- **Propósito:** Componente envoltorio (wrapper) de utilidades animadas. Todo hijo (`children`) envuelto aquí, aparecerá con una suave traslación y desvanecimiento vertical impulsado por `framer-motion`.
- **Props:** `children`, `delay` (float opcional), `className`.
- **Dependencias:** `framer-motion`.

## Componentes del Conversor (`components/conversor/`)

### `conversor-client.tsx`
- **Propósito:** El formulario principal. Mantiene el estado global del modo (`"stereo"` vs `"tetra_4mic"`) a través de componentes `<Tabs>`, rastrea el archivo adjunto, maneja banderas booleanas como `isConverting` (bloqueando clics durante la espera) y renderiza `AudioResult` si la petición fue exitosa.
- **Estado:** `file` (File), `mode` (string), `isConverting` (boolean), `result` (object).
- **Dependencias:** `lib/api.ts` -> `convertAudio(file, mode)`.

### `file-dropzone.tsx`
- **Propósito:** Interfaz interactiva de "Arrastrar y Soltar" o explorador estándar de archivos para subir audios. 
- **Props:** `onFileSelect` (callback ejecutado cuando el File se adjunta válidamente) y `accept` (string para filtrar formatos, default: `audio/*`).
- **Estado:** `isDragActive` (bool que tiñe de color primario el recuadro cuando un archivo sobrevuela el área).

### `audio-result.tsx`
- **Propósito:** Componente que se renderiza con éxito para desglosar la matriz de resultados JSON que envió el backend tras la conversión. Parsea las rutas e inyecta elementos `<audio controls src="...">` nativos HTML y botones de enlace directo `<a>` con la propiedad `download` para descargar el WAV o MP3 resultante.

## Componentes de Demo (`components/demo/`)

### `demo-client.tsx`
- **Propósito:** Engloba la interfaz compleja del área de pruebas.
- **Estado:** Controla a través de `useState` múltiple (o useReducer) los estados de:
  - `direccion` (Slider azimut)
  - `altura` (Slider elevación)
  - `apertura` (Slider amplitud)
  - `movimiento` (Slider rotación automatizada)
- **Flujo:** Envía el input del usuario al backend a través de `api.ts` -> `runDemo(file, direccion, altura, apertura, movimiento)` y, con el resultado, pinta reproductores. Paralelamente inyecta estos mismos valores (estados de React) hacia abajo como props al componente de la escena para actualizar el visor gráfico sin necesidad de esperar a la API.

### `visualizer-3d.tsx`
- **Propósito:** Lienzo 3D. (Documentado a profundidad en `docs/06_Demo3D.md`).

## Componentes de la Guía y Home (`components/home/`, `components/guia/`)

### `hero.tsx` y `options-section.tsx`
- **Propósito:** Interfaz puramente gráfica para el Landing.
- **Opciones:** Contiene arreglos estáticos (JS vanilla arrays) con la copia ("¿Cómo funciona?", "¿Qué obtienes?") renderizados a través de la función `map()` y envueltos en Glassmorphism (sombras suaves de CSS, `backdrop-blur`).

### `guia-content.tsx`
- **Propósito:** Contenedor gráfico de las ayudas conceptuales para explicar Ambisonics y FOA en idioma no técnico y para mostrar las diferencias (Opción 1 vs Opción 2).
