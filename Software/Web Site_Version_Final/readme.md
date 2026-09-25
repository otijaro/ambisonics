# Ambisonic Audio Processor 

Aplicación web para el procesamiento espacial de audio utilizando tecnología Ambisonic, HRTF y un frontend interactivo en Next.js.

## Requisitos Previos
- **Node.js**: v18 o superior (se recomienda usar pnpm o 
pm).
- **Python**: 3.9 o superior.
- **Git**
- **FFmpeg**: Obligatorio. El backend (en processor.py y demo_processor.py) utiliza subprocess para llamar directamente a FFmpeg y procesar/exportar los resultados en formato MP3.
  - **Windows**: Descargar desde [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) y agregarlo al PATH del sistema.
  - **Mac**: rew install ffmpeg
  - **Linux**: sudo apt install ffmpeg
- **Archivo HRTF**: Es esencial contar con el archivo de respuesta impulsional (HRIR/HRTF). El proyecto espera obligatoriamente encontrar el archivo **hrtf.sofa** dentro de la carpeta Codigos/. *(Nota: este archivo de ~3.3MB ya ha sido incluido en el repositorio para facilitar la ejecución).*

## Instalación

### 1. Clonar el repositorio
\\\ash
git clone https://github.com/tu-usuario/ambisonic_github.git
cd ambisonic_github
\\\

### 2. Configurar y levantar el Backend (Python)
\\\ash
# Crear y activar entorno virtual
python -m venv venv
# En Windows: venv\Scripts\activate
# En Mac/Linux: source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
\\\

### 3. Configurar y levantar el Frontend (Next.js)
En una nueva terminal, vuelve a la raíz del proyecto:
\\\ash
npm install
\\\

## Variables de Entorno
Crea un archivo .env en la raíz (puedes guiarte por .env.example).
\\\env
NEXT_PUBLIC_API_URL=http://localhost:8000
\\\

## Ejecución en Local
Para arrancar el proyecto en modo desarrollo, necesitas dos procesos en paralelo:

1. **Backend**:
\\\ash
# Asegúrate de tener tu entorno virtual activo
uvicorn backend.main:app --host 0.0.0.0 --port 8000
\\\

2. **Frontend**:
\\\ash
# Desde la raíz del proyecto
npm run dev
\\\
La aplicación estará disponible en http://localhost:3000.

## Estructura de Tests
Los scripts de prueba y validación de memoria se encuentran en la carpeta 	ests/.

## Solución de errores comunes
- **Error CORS al subir un archivo**: Asegúrate de que NEXT_PUBLIC_API_URL apunte exactamente al puerto que corre uvicorn (por defecto 8000).
- **Falta el módulo X en Python**: Verifica que activaste tu entorno virtual y corriste pip install -r requirements.txt.
- **Error de FileNotFound relacionado a FFmpeg**: Verifica que instalaste FFmpeg y que el ejecutable está agregado a las variables de entorno PATH, de manera que pueda ser invocado con fmpeg desde la terminal.
- **Error FileNotFound relacionado a SOFA**: Si el backend falla al iniciar o procesar, asegúrate de que el archivo exista exactamente en la ruta Codigos/hrtf.sofa respecto a la raíz del backend.
