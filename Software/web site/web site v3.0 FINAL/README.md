# Ambisonic — Plataforma Web de Audio Espacial y Codificación Ambisónica

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-16.2-black.svg)](https://nextjs.org/)
[![React](https://img.shields.io/badge/React-19-61dafb.svg)](https://react.dev/)
[![Ambisonics](https://img.shields.io/badge/Ambisonics-FOA%20AmbiX%20(SN3D)-purple.svg)](https://en.wikipedia.org/wiki/Ambisonics)
[![HRIR](https://img.shields.io/badge/HRIR-SADIE%20II%20D1-orange.svg)](https://www.york.ac.uk/sadie-project/)

Ambisonic es una plataforma web integral para el procesamiento, conversión y experimentación con audio espacial tridimensional. El sistema permite transformar pistas de audio estéreo convencional y grabaciones de arreglos tetraédricos de cuatro micrófonos en campos sonoros ambisónicos de primer orden (**FOA**, *First-Order Ambisonics*) bajo el estándar **AmbiX** (orden ACN, normalización SN3D), decodificándolos analíticamente a formatos binaurales inmersivos de alta fidelidad mediante el decodificador **SAD** (*Sampling Ambisonic Decoder*) y la base de datos acústica **SADIE II (sujeto D1)**.

---

## Índice

1. [Objetivo del Proyecto](#1-objetivo-del-proyecto)
2. [Funcionalidades Principales](#2-funcionalidades-principales)
3. [Arquitectura y Tecnologías](#3-arquitectura-y-tecnologías)
4. [Requisitos Previos](#4-requisitos-previos)
5. [Estructura del Repositorio](#5-estructura-del-repositorio)
6. [Instalación Paso a Paso](#6-instalación-paso-a-paso)
7. [Configuración de Base de Datos PostgreSQL](#7-configuración-de-base-de-datos-postgresql)
8. [Gestión y Verificación de Bases HRIR SADIE II D1](#8-gestión-y-verificación-de-bases-hrir-sadie-ii-d1)
9. [Ejecución Local de la Plataforma](#9-ejecución-local-de-la-plataforma)
10. [Guía de Uso: Conversor y Demo Interactiva](#10-guía-de-uso-conversor-y-demo-interactiva)
11. [Formatos y Frecuencias Nativas Admitidas](#11-formatos-y-frecuencias-nativas-admitidas)
12. [Especificaciones del Archivo FOA AmbiX](#12-especificaciones-del-archivo-foa-ambix)
13. [Solución de Problemas Frecuentes](#13-solución-de-problemas-frecuentes)
14. [Referencias Científicas y Atribuciones](#14-referencias-científicas-y-atribuciones)
15. [Condiciones de Autoría y Licencia](#15-condiciones-de-autoría-y-licencia)

---

## 1. Objetivo del Proyecto

El proyecto tiene como propósito democratizar el acceso y la comprensión del audio espacial inmersivo tanto para investigadores, ingenieros de sonido y músicos, como para usuarios sin formación técnica avanzada. La plataforma resuelve la brecha entre las formulaciones matemáticas rigurosas del campo acústico (armónicos esféricos, matrices ortogonales, coherencia espectral) y una experiencia de usuario interactiva y accesible desde el navegador web.

---

## 2. Funcionalidades Principales

- **Opción 1: Conversión Estéreo a FOA (AmbiX):**
  - Análisis tiempo-frecuencia mediante STFT (*Short-Time Fourier Transform*, ventana Hann a 2048 muestras).
  - Estimación de coherencia espectral local **MSC** (*Magnitude Squared Coherence*, ventana temporal de 100 ms) para segregar componentes acústicas directas de difusas.
  - Preservación matemáticamente demostrada de la componente lateral *Side* ($S = \frac{L - R}{2}$) proyectada en el canal $Y = S \cdot \cos(\text{elevación})$ para evitar pérdida de información ante señales en oposición de fase.
- **Opción 2: Conversión Tetraédrica de 4 Micrófonos a FOA:**
  - Decodificación analítica en campo libre de cápsulas en Formato A canónico: **FLU** (*Front-Left-Up*), **FRD** (*Front-Right-Down*), **BLD** (*Back-Left-Down*) y **BRU** (*Back-Right-Up*).
  - Transformación matricial ortogonal canónica a Formato B (AmbiX SN3D).
- **Decodificador Binaural SAD (Geometría B Octaédrica):**
  - Proyección sobre 6 altavoces virtuales distribuidos en cruz simétrica tridimensional ($\pm X, \pm Y, \pm Z$).
  - Convolución temporal particionada (*Overlap-Add*) con respuestas impulsionales **HRIR** (*Head-Related Impulse Response*) de la base de datos **SADIE II (Sujeto D1)**.
  - Procesamiento nativo y exacto a **44.1 kHz, 48 kHz y 96 kHz** sin remuestreo forzado.
- **Generación de Múltiples Salidas:**
  - **Binaural Estándar:** Audio espacial fiel con nivel pico controlado a 0.95 (−0.45 dBFS) para audífonos convencionales.
  - **Binaural 3D Perceptual:** Espacialización dinámica con modulación orbital y estabilización perceptual de *loudness*.
  - **Master FOA AmbiX:** Archivo WAV multicanal de 4 pistas en orden ACN $[W, Y, Z, X]$ y normalización SN3D para postproducción profesional en DAWs (Reaper, Pro Tools), motores de videojuegos (Unity, Unreal) y video 360°/VR.
- **Demo Interactiva en Tiempo Real:**
  - Cuatro controles directos: **Dirección** (Azimut $-180^\circ$ a $+180^\circ$), **Altura** (Elevación $-90^\circ$ a $+90^\circ$), **Apertura** (Extensión lateral $0\%$ a $100\%$) y **Movimiento** (Órbita 3D $0\%$ a $100\%$).
  - Procesamiento ágil de fragmentos de hasta 15 segundos para retroalimentación instantánea.
- **Sistema de Cuentas y «Mis Conversiones»:**
  - Autenticación con contraseñas cifradas en *bcrypt*.
  - Historial de conversiones personales con retención temporal de 24 horas y limpieza automática en segundo plano.

---

## 3. Arquitectura y Tecnologías

La plataforma sigue una arquitectura desacoplada y modular:

```
[ Navegador Web ]  <--->  [ Frontend: Next.js 16 (App Router) ]
                                   | (Proxy /api/*)
                                   v
                          [ Backend: FastAPI (Python 3.10+) ]
                           ├── Motor DSP (NumPy / SciPy / SOFA)
                           ├── Decodificador SAD (SADIE II D1)
                           └── Base de Datos (PostgreSQL / SQLAlchemy)
```

- **Frontend:** Next.js 16 (React 19), Tailwind CSS v4, Lucide Icons, Framer Motion, Three.js / React Three Fiber.
- **Backend:** FastAPI, Uvicorn, SQLAlchemy ORM, Pydantic v2, Python-dotenv.
- **Procesamiento de Audio y DSP:** NumPy, SciPy (Signal/STFT), SoundFile (libsndfile), Pysofaconventions (netCDF4 / SOFA estándar AES69).
- **Base de Datos:** PostgreSQL (local o servicio en la nube como Neon / Supabase).
- **Codificación MP3:** FFmpeg (opcional, requerido únicamente para generar archivos `.mp3` a $\le 48\text{ kHz}$).

---

## 4. Requisitos Previos

Antes de instalar la aplicación, asegúrate de tener instalado en tu sistema:

1. **Python:** Versión **3.10**, **3.11** o **3.12** ([Descargar Python](https://www.python.org/downloads/)).
2. **Node.js:** Versión **20.9 o superior** (LTS recomendado: Node.js 20.x o 22.x; requisito mandatario de Next.js 16). ([Descargar Node.js](https://nodejs.org/)).
3. **Gestor de paquetes:** `pnpm` versión 9.x, 10.x o superior recomendado (`npm install -g pnpm`), o alternativamente `npm` (v10+).
4. **PostgreSQL:** Versión **14+** local instalada y en ejecución, o una URL de conexión a una instancia en la nube.
5. **FFmpeg (Opcional):** Para la exportación de previsualizaciones MP3 a 320 kbps. Si no está instalado, la plataforma generará todas las salidas en formato WAV de alta fidelidad sin interrumpir el funcionamiento.

---

## 5. Estructura del Repositorio

```
pagina_github/
├── app/                        # Rutas de Next.js (App Router)
│   ├── (auth)/                 # Rutas de autenticación (login, registro)
│   ├── api/[...proxy]/         # Proxy HTTP interno hacia el backend FastAPI
│   ├── conversor/              # Página del conversor de audio
│   ├── demo/                   # Página de la demo interactiva
│   ├── guia/                   # Documentación técnica interactiva
│   ├── mis-conversiones/       # Panel de historial de usuario
│   ├── globals.css             # Estilos globales y paleta aurora
│   ├── layout.tsx              # Layout raíz con Navbar y Footer
│   └── page.tsx                # Página de inicio (Landing)
├── backend/                    # Servidor de procesamiento de audio
│   ├── routers/                # Endpoints de autenticación y conversiones
│   ├── services/               # Tarea de limpieza periódica de temporales (24h)
│   ├── sofa/                   # Directorio de bases HRIR SADIE II D1 (.sofa)
│   ├── static/                 # Almacenamiento temporal de conversiones
│   ├── utils/                  # Hashing bcrypt y tokens seguros
│   ├── core_dsp.py             # Algoritmos matemáticos FOA, SAD, MSC y OLA
│   ├── database.py             # Conexión SQLAlchemy a PostgreSQL
│   ├── demo.py                 # Funciones de rotación y órbita 3D de la demo
│   ├── demo_processor.py       # Procesador de demos de 15 segundos
│   ├── dependencies.py         # Inyección de dependencias de usuario
│   ├── main.py                 # Aplicación principal FastAPI y ciclo de vida
│   ├── models.py               # Modelos relacionales de base de datos
│   ├── processor.py            # Orquestador del pipeline de conversión OLA
│   └── schemas.py              # Esquemas Pydantic de validación
├── components/                 # Componentes reutilizables de React
│   ├── conversor/              # Cliente interactivo de conversión y tarjetas FOA
│   ├── demo/                   # Controles y visualizador 3D de la demo
│   ├── guia/                   # Contenido estructurado de la guía
│   ├── ui/                     # Botones, sliders, diálogos y tarjetas glass
│   └── ...
├── lib/                        # Clientes API y utilidades del frontend
├── public/                     # Recursos multimedia estáticos (imágenes, iconos)
├── scripts/                    # Scripts de utilidad y diagnóstico
│   ├── init_db.py              # Inicialización de tablas en PostgreSQL
│   ├── setup_sofa.py           # Verificación e instalación de bases SADIE II D1
│   └── test_distribution.py    # Suite de pruebas automatizadas con señales sintéticas
├── .env.example                # Plantilla de variables de entorno
├── .gitignore                  # Reglas de exclusión para Git
├── package.json                # Dependencias del frontend
├── pnpm-lock.yaml              # Archivo de bloqueo de dependencias pnpm
├── requirements.txt            # Dependencias Python del backend
├── run_backend.bat / .sh       # Lanzador rápido del backend
├── run_frontend.bat / .sh      # Lanzador rápido del frontend
└── README.md                   # Este manual de documentación
```

---

## 6. Instalación Paso a Paso

### Paso 1: Clonar el Repositorio
```bash
git clone https://github.com/tu-usuario/ambisonic.git
cd ambisonic
```

### Paso 2: Configurar el Entorno Virtual de Python (Backend)
```bash
# En Windows (PowerShell):
python -m venv .venv
.\.venv\Scripts\activate

# En Linux o macOS:
python3 -m venv .venv
source .venv/bin/activate
```

Instalar las dependencias de Python:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Paso 3: Instalar Dependencias de Node.js (Frontend)
```bash
pnpm install
# O si utilizas npm:
# npm install
```

### Paso 4: Configurar Variables de Entorno
Copia el archivo `.env.example` creando el archivo `.env`:
```bash
# En Windows (PowerShell):
Copy-Item .env.example .env

# En Linux o macOS:
cp .env.example .env
```

Abre el archivo `.env` con tu editor y ajusta la variable `DATABASE_URL` con tu cadena de conexión a PostgreSQL (ver siguiente sección).

---

## 7. Configuración de Base de Datos PostgreSQL

Ambisonic requiere PostgreSQL para gestionar el registro de usuarios, las sesiones de autenticación y el historial de descargas.

### Opción A: PostgreSQL Local
1. Abre tu consola de PostgreSQL (`psql`) o herramienta gráfica (pgAdmin, DBeaver) y crea una base de datos:
   ```sql
   CREATE DATABASE ambisonic_db;
   ```
2. Configura tu `.env`:
   ```env
   DATABASE_URL=postgresql://postgres:tu_password@localhost:5432/ambisonic_db
   ```

### Opción B: PostgreSQL en la Nube (Gratuito con Neon o Supabase)
1. Crea un proyecto en [Neon.tech](https://neon.tech/) o [Supabase](https://supabase.com/).
2. Copia la cadena de conexión suministrada en tu panel y pégala en `.env`:
   ```env
   DATABASE_URL=postgresql://usuario:contraseña@ep-ejemplo.sa-east-1.aws.neon.tech/neondb?sslmode=require
   ```

### Inicializar las Tablas
Ejecuta el script automatizado para crear todas las tablas requeridas:
```bash
python scripts/init_db.py
```
El script reportará la creación exitosa de las tablas `users`, `user_sessions` y `processing_requests`.

---

## 8. Gestión y Verificación de Bases HRIR SADIE II D1

El decodificador SAD requiere tres archivos en formato AES69 SOFA correspondientes al **Sujeto D1** de la base de datos acústica **SADIE II** medida por el AudioLab de la Universidad de York.

### Licencia y Atribución
Los archivos SOFA de SADIE II se distribuyen oficialmente bajo la licencia **Apache License, Version 2.0** (Copyright 2018, University of York). Esta licencia permite expresamente su uso, reproducción y distribución libremente con atribución.

### Archivos Requeridos y Sumas de Verificación (SHA-256)
Los tres archivos deben ubicarse en `backend/sofa/`:

| Frecuencia | Nombre de Archivo | Tamaño | Suma de Comprobación SHA-256 |
| :--- | :--- | :--- | :--- |
| **44.1 kHz** | `D1_44K_16bit_256tap_FIR_SOFA.sofa` | ~34.6 MB | `efffbf7f8e963c8162f24f44944ed6f8a44f5d3c546e76a4d74a650a0e3766d2` |
| **48 kHz** | `D1_48K_24bit_256tap_FIR_SOFA.sofa` | ~34.6 MB | `9af7cb19531e52fb7ae8ec92621e6ab62b1d5fe584b3742be36699a0ddb0ccd4` |
| **96 kHz** | `D1_96K_24bit_512tap_FIR_SOFA.sofa` | ~69.0 MB | `49c46541517cd8c43927297fc9106b8a9aee7aec25c3a6ba6d144b6da2f98983` |

### Verificación e Integridad Local
Para comprobar que los archivos están en su lugar y que sus sumas de verificación coinciden con los registros oficiales:
```bash
python scripts/setup_sofa.py
```

*Nota para GitHub:* Si clonas el repositorio desde un entorno donde los binarios pesados están excluidos vía `.gitignore`, el script verificará la presencia local y la integridad criptográfica de cada archivo. En caso de ausencia, el script proporciona de manera transparente el enlace oficial directo de Zenodo ([D1_HRIR_SOFA.zip](https://zenodo.org/records/12092466/files/D1_HRIR_SOFA.zip?download=1)) y las instrucciones detalladas de extracción en `backend/sofa/`, garantizando una configuración confiable sin depender de descargas desatendidas o no autenticadas.

---

## 9. Ejecución Local de la Plataforma

Para operar la plataforma completa se deben iniciar dos procesos simultáneos: el backend (FastAPI) y el frontend (Next.js).

### Terminal 1: Iniciar el Backend (Puerto 8000)
```bash
# Windows:
.\run_backend.bat
# O manualmente:
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# Linux/macOS:
chmod +x run_backend.sh
./run_backend.sh
```
El backend cargará en memoria RAM las bases SOFA y reportará: `Uvicorn running on http://0.0.0.0:8000`.

### Terminal 2: Iniciar el Frontend (Puerto 3000)
```bash
# Windows:
.\run_frontend.bat
# O manualmente:
pnpm dev

# Linux/macOS:
chmod +x run_frontend.sh
./run_frontend.sh
```

Abre tu navegador web e ingresa a: **`http://localhost:3000`**.

---

## 10. Guía de Uso: Conversor y Demo Interactiva

### Conversor Principal (`/conversor`)
1. **Cargar Audio:** Arrastra o selecciona tu archivo de audio (WAV o MP3) en el dropzone.
2. **Seleccionar Modo de Entrada:**
   - **Opción 1 (Estéreo):** Para pistas estándar de 2 canales. Extrae el campo 3D conservando la separación estéreo y la componente lateral.
   - **Opción 2 (4 Micrófonos Tetraédrico):** Para grabaciones multicanal con cápsulas físicas orientadas en [FLU, FRD, BLD, BRU].
3. **Procesar:** Haz clic en «Iniciar conversión espacial».
4. **Escuchar y Descargar:**
   - Reproduce y compara el audio original frente a las versiones **Binaural Estándar** y **Binaural 3D**.
   - Descarga el audio binaural en WAV o MP3, o descarga directamente el archivo maestro **FOA (.wav de 4 canales)**.

### Demo Interactiva (`/demo`)
1. Carga una pista corta o selecciona la muestra incluida.
2. Modifica en tiempo real los cuatro controles espaciales:
   - **Dirección (Azimut):** Desplaza la fuente en el plano horizontal (0° frente, +90° izquierda, −90° derecha, ±180° atrás).
   - **Altura (Elevación):** Eleva la fuente hacia el cenit (+90°) o hacia el suelo (−90° nadir).
   - **Apertura:** Modula la amplitud estéreo (0% señal puntual, 100% máxima amplitud).
   - **Movimiento:** Activa una rotación orbital 3D continua alrededor de la posición seleccionada.
3. Observa la representación en la esfera tridimensional interactiva y escucha el resultado binaural espacializado.

---

## 11. Formatos y Frecuencias Nativas Admitidas

- **Formatos de Entrada:**
  - **WAV:** PCM entero de 16 o 24 bits, coma flotante de 32 bits (IEEE Float).
  - **MP3:** Archivos codificados a cualquier tasa de bits estándar.
- **Frecuencias de Muestreo Compatibles:**
  - **44,100 Hz (44.1 kHz)**
  - **48,000 Hz (48 kHz)**
  - **96,000 Hz (96 kHz)**
- **Procesamiento Nativo sin Remuestreo:**
  La plataforma valida la frecuencia nativa del archivo y selecciona dinámicamente el perfil HRIR medido a esa misma tasa, garantizando que el audio conserve íntegra su respuesta espectral original sin artefactos de interpolación o pérdidas en alta frecuencia.

---

## 12. Especificaciones del Archivo FOA AmbiX

El archivo descargable denominado `output_foa.wav` contiene el campo ambisónico de primer orden sin decodificar a dos canales. Cumple rigurosamente con los estándares de la industria del audio espacial:

- **Formato Contenedor:** WAV (Broadcast Wave Format compatible, PCM 16 bits).
- **Número de Canales:** Exactamente 4 canales en un único archivo polifónico.
- **Orden de Canales (ACN):**
  - **Canal 0 (W):** Patrón omnidireccional (presión acústica de orden 0).
  - **Canal 1 (Y):** Dipolo horizontal lateral (figura de 8, izquierda − derecha).
  - **Canal 2 (Z):** Dipolo vertical (figura de 8, arriba − abajo).
  - **Canal 3 (X):** Dipolo frontal (figura de 8, adelante − atrás).
- **Convención de Normalización:** **SN3D** (Schmidt Semi-Normalization).
- **Compatibilidad:** Compatible con plugins VST/AU ambisónicos (IEM Plug-in Suite, SPARTA, ambiX de Matthias Kronlachner), decodificadores para YouTube 360 y motores de Realidad Virtual (SteamVR Audio, Meta Spatial Audio SDK).

---

## 13. Solución de Problemas Frecuentes

### 1. Error: `No se encontró el archivo SOFA SADIE II D1 para XX Hz`
- **Causa:** Faltan los archivos `.sofa` en la carpeta `backend/sofa/`.
- **Solución:** Ejecuta `python scripts/setup_sofa.py` para verificar cuáles faltan e instálalos desde la fuente oficial siguiendo las instrucciones en pantalla.

### 2. Error: `No se encontró DATABASE_URL. Configura la conexión a PostgreSQL.`
- **Causa:** El archivo `.env` no existe o no contiene la variable `DATABASE_URL`.
- **Solución:** Copia `.env.example` como `.env` y configura una cadena válida de PostgreSQL.

### 3. Error: `relation "users" does not exist`
- **Causa:** No se han inicializado las tablas en la base de datos PostgreSQL.
- **Solución:** Ejecuta `python scripts/init_db.py` para crear las tablas automáticamente.

### 4. Error: `Frecuencia de muestreo no soportada: XX Hz`
- **Causa:** Se subió un archivo a una tasa no estándar (por ejemplo 22,050 Hz o 88,200 Hz).
- **Solución:** Utiliza archivos a 44.1 kHz, 48 kHz o 96 kHz.

### 5. Las conversiones se demoran o consumen demasiada CPU
- **Causa:** El equipo tiene recursos limitados y `MAX_CONCURRENT_DSP` está muy alto.
- **Solución:** En `.env`, establece `MAX_CONCURRENT_DSP=1`.

---

## 14. Referencias Científicas y Atribuciones

El diseño matemático y acústico de la plataforma se fundamenta en la siguiente literatura especializada:

1. **Zotter, F., & Frank, M. (2019).** *Ambisonics: A Practical Guide to Practical Theory*. Springer Topics in Signal Processing, Vol. 19. Springer Cham. [DOI: 10.1007/978-3-030-26493-2](https://doi.org/10.1007/978-3-030-26493-2).
   - Formulación analítica del *Sampling Ambisonic Decoder* (SAD, Cap. 4, Ec. 4.39) adaptado a ACN/SN3D sobre geometrías poliedrales regulares y semirregulares.
2. **Armstrong, C. M., Thresh, A. J., Murphy, D. T., & Kearney, G. (2018).** *A Perceptual Evaluation of Individual and Non-Individual HRTFs on Horizontal Localisation Accuracy*. Applied Sciences, 8(11), 2029. [DOI: 10.3390/app8112029](https://doi.org/10.3390/app8112029).
   - Base de datos de alta resolución SADIE II (Sujeto D1, cabeza de maniquí acústico KEMAR/KU100). Licenciada bajo Apache License 2.0 por la Universidad de York.
3. **Pulkki, V. (2007).** *Spatial Sound Reproduction with Directional Audio Coding*. Journal of the Audio Engineering Society (JAES), 55(6), 503–516.
   - Principios de descomposición espectral tiempo-frecuencia en componentes directas y difusas mediante estimadores de coherencia temporal.
4. **Nachbar, C., Zotter, F., Deleflie, E., & Sontacchi, A. (2011).** *ambiX - A Suggested Ambisonics Format*. Proceedings of the Ambisonics Symposium 2011, Lexington, KY.
   - Especificación del estándar AmbiX (secuencia de canales ACN y normalización de armónicos esféricos SN3D).

---

## 15. Condiciones de Autoría y Licencia

- **Autoría del Proyecto y Trabajo de Grado:** Desarrollado como parte integral de investigación académica en ingeniería y tecnologías de audio espacial.
- **Base de Datos SADIE II D1:** Copyright © 2018 University of York AudioLab. Distribuida bajo la licencia [Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0).
- **Código del Repositorio:** El software se suministra con fines académicos y de investigación. Para consultas sobre derechos de autor, adaptaciones o uso en proyectos derivados, contactar a los autores a través del repositorio oficial de GitHub.

