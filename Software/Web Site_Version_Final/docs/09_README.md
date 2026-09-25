# Ambisonic 🎧🌌

![Ambisonic Banner](../public/home.png)

> **Ambisonic** es una plataforma web innovadora diseñada para transformar audios estéreo planos en verdaderas experiencias de sonido espacial inmersivas. Utilizando procesamientos matemáticos rigurosos y respuestas de impulso binaurales (HRTF), la plataforma permite escuchar el espacio en 360 grados usando cualquier par de audífonos convencionales.

## ✨ Características Principales

*   **Conversión Rápida (Estéreo a FOA):** Mapeo de energía direccional estéreo hacia algoritmos Ambisonics de Primer Orden (W, X, Y, Z).
*   **Decodificador de Arreglos (Tetraédrico a FOA):** Soporte nativo para grabaciones directas obtenidas desde un ensamble real de cuatro cápsulas de micrófono.
*   **Binauralización HRTF:** Escucha el sonido con noción de Elevación y Azimut a través de convolución de audio precisa.
*   **Demo Interactiva con Visualizador 3D:** Un lienzo reactivo potenciado por Three.js en el cual los usuarios pueden modificar a voluntad y en tiempo real la dirección, altura y apertura del audio.
*   **Multiplataforma Web:** Frontend responsivo y amigable para el usuario desarrollado en Next.js.
*   **Resultados Múltiples:** Exporta asíncronamente en alta calidad a WAV (.wav) para producción y MP3 (.mp3) para compartibilidad instantánea.

## 🏗️ Arquitectura y Tecnologías

Ambisonic consta de un sistema asíncrono y desacoplado, logrando separar la costosa carga del DSP a un servidor en Python, sin degradar el rendimiento y fluidez del frontend interactivo de React.

*   **Frontend:** Next.js (App Router), React 19, TypeScript, Tailwind CSS, Framer Motion.
*   **Motor 3D Visual:** Three.js, React Three Fiber.
*   **Backend (API Rest):** Python, FastAPI, Uvicorn, Python-Multipart.
*   **Procesamiento de Señales (DSP):** NumPy, SciPy (STFT/Convoluciones), SoundFile.
*   **Codificación Media:** Subprocess FFmpeg nativo.

Para conocer más sobre la matemática subyacente y la comunicación de componentes, visita nuestra [Documentación Técnica (Carpeta /docs)](./README.md).

## 🚀 Instalación y Despliegue Local

### Prerrequisitos
- Python 3.10 o superior (con `pip`)
- Node.js 18.x o superior (con `npm` o `pnpm`)
- Sistema Operativo que soporte FFmpeg (para exportar MP3).

### Levantar el Backend (FastAPI)
1. Instalar requerimientos y levantar servidor:
   ```bash
   python -m venv venv
   source venv/bin/activate  # venv\Scripts\activate en Windows
   pip install -r requirements.txt
   uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
   ```

### Levantar el Frontend (Next.js)
1. En otra terminal, en la raíz del proyecto, instala las dependencias de Node:
   ```bash
   npm install
   ```
2. Asegúrate de tener la variable de entorno `NEXT_PUBLIC_API_URL` apuntando a la dirección del backend. Puedes crear un `.env.local`:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```
3. Ejecutar entorno de desarrollo web:
   ```bash
   npm run dev
   ```

El proyecto estará corriendo en [http://localhost:3000](http://localhost:3000).

## 📖 Uso
Navega a la página web y prueba el **Conversor**. Sube un archivo WAV o MP3 y selecciona si el audio original es estéreo o una captura multicanal tetraédrica. Presiona "Convertir" y espera a que el motor aplique los filtros y devuelva un reproductor inmersivo binaural. 
Adicionalmente, prueba nuestra **Guía** y **Demo 3D** si necesitas interactuar manualmente con los parámetros físicos en lugar del modo de rotación perceptual fijo.

## 👩‍💻 Autores
Proyecto concebido y desarrollado por:
- **Sharon Catalina Vargas Cortes**
- **Anwar Andrés Cuello Pabón**

**Directores:** Omar Javier Tíjaro Rojas & Nicolás Esteban Hernández Bustos.  
*Universidad Industrial de Santander (UIS).*

## 📄 Licencia
[Ver detalles de licencia, típicamente MIT / Prohibición Comercial Universitaria].
