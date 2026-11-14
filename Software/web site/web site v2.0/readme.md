# Ambisonic Audio Processor

Aplicación web para procesamiento espacial de audio utilizando tecnología Ambisonic, HRTF y procesamiento digital de señales (DSP).

La plataforma permite cargar archivos de audio, realizar conversiones espaciales y escuchar resultados con percepción tridimensional mediante modelos acústicos HRTF.

El sistema está compuesto por dos partes:

- **Frontend:** Página web interactiva desarrollada con Next.js y React.
- **Backend:** Servidor desarrollado en Python con FastAPI encargado del procesamiento de audio.

---

# Instalación y ejecución de la plataforma

Esta guía explica cómo instalar la aplicación desde cero en un computador nuevo.

Para ejecutar correctamente la plataforma se deben instalar algunos programas, descargar el proyecto y ejecutar simultáneamente el servidor de procesamiento y la página web.

---

# 1. Instalación de programas necesarios

Antes de descargar el proyecto, instalar los siguientes programas.

---

## 1.1 Instalar Git

Git permite descargar y actualizar el proyecto desde GitHub.

Descargar:

https://git-scm.com/downloads

Después de instalarlo, verificar la instalación:

```bash
git --version
```

Debe aparecer la versión instalada de Git.

---

## 1.2 Instalar Python

Python permite ejecutar el servidor encargado del procesamiento de audio.

Descargar:

https://www.python.org/downloads/

Durante la instalación en Windows activar la opción:

```
Add Python to PATH
```

Verificar:

```bash
python --version
```

Debe aparecer una versión de Python 3.9 o superior.

---

## 1.3 Instalar Node.js

Node.js permite ejecutar la interfaz web desarrollada en Next.js.

Descargar la versión LTS:

https://nodejs.org/

Verificar:

```bash
node --version
```

y:

```bash
npm --version
```

---

## 1.4 Instalar FFmpeg

FFmpeg es utilizado por el backend para procesar y exportar archivos de audio en formato MP3.

Descargar para Windows:

https://www.gyan.dev/ffmpeg/builds/

Después de instalarlo verificar:

```bash
ffmpeg -version
```

Si aparece información de la versión, FFmpeg está correctamente instalado.

---

# 2. Descargar el proyecto

Abrir una terminal (PowerShell en Windows).

Ubicarse en la carpeta donde se desea guardar el proyecto.

Ejemplo:

```bash
cd Downloads
```

Clonar el repositorio:

```bash
git clone https://github.com/otijaro/ambisonics.git
```

Ingresar al repositorio:

```bash
cd ambisonics
```

Ingresar a la versión de la plataforma web:

```bash
cd "Software/Web Site_Version_Final"
```

---

# 3. Configuración del Backend

El backend es el servidor encargado de recibir los audios, ejecutar el procesamiento Ambisonic y generar los archivos de salida.

---

## 3.1 Crear entorno virtual de Python

Ejecutar:

```bash
python -m venv venv
```

Esto crea un entorno independiente donde se instalarán las librerías necesarias.

---

## 3.2 Activar entorno virtual

### Windows:

```bash
venv\Scripts\activate
```

### Linux/Mac:

```bash
source venv/bin/activate
```

Cuando el entorno esté activo aparecerá algo similar:

```
(venv)
```

al inicio de la terminal.

---

## 3.3 Instalar dependencias del backend

Ejecutar:

```bash
pip install -r requirements.txt
```

Este comando instala automáticamente todas las librerías necesarias para el funcionamiento del servidor.

---

# 4. Archivo HRTF necesario

El sistema utiliza información acústica HRTF para generar la sensación de espacialidad del audio.

El archivo requerido es:

```
Codigos/hrtf.sofa
```

Este archivo ya está incluido dentro del repositorio.

No debe cambiarse de ubicación.

---

# 5. Configuración de variables de entorno

Dentro de la carpeta:

```
Web Site_Version_Final
```

crear un archivo llamado:

```
.env
```

Agregar:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Esta variable permite que la página web se comunique con el backend.

---

# 6. Ejecutar el Backend

Con el entorno virtual activado, ejecutar:

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Si la ejecución es correcta aparecerá:

```
Application startup complete
```

El backend estará funcionando en:

```
http://localhost:8000
```

Mantener esta terminal abierta.

---

# 7. Instalación del Frontend (Página Web)

Abrir una nueva terminal.

Ingresar nuevamente a la carpeta del proyecto:

```bash
cd "Software/Web Site_Version_Final"
```

Instalar las dependencias de la página web:

```bash
npm install
```

Este proceso instala todos los paquetes necesarios de Next.js, React y la interfaz gráfica.

---

# 8. Ejecutar la página web

Después de instalar las dependencias:

```bash
npm run dev
```

Si funciona correctamente aparecerá:

```
Local: http://localhost:3000
```

Abrir el navegador y entrar a:

```
http://localhost:3000
```

La plataforma estará disponible.

---

# 9. Ejecución normal después de la instalación

Una vez realizada la instalación inicial, para iniciar nuevamente la plataforma solamente se necesitan dos terminales.

---

## Terminal 1: Backend

```bash
cd "Software/Web Site_Version_Final"

venv\Scripts\activate

uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

---

## Terminal 2: Frontend

```bash
cd "Software/Web Site_Version_Final"

npm run dev
```

Luego abrir:

```
http://localhost:3000
```

---

# Estructura del proyecto

```
Web Site_Version_Final

├── app/
│   └── Páginas principales de la aplicación web

├── components/
│   └── Componentes visuales de la interfaz

├── backend/
│   ├── API FastAPI
│   └── Procesamiento digital de audio

├── Codigos/
│   └── Archivos auxiliares y HRTF

├── public/
│   └── Imágenes y recursos multimedia

├── lib/
│   └── Comunicación frontend-backend

├── tests/
│   └── Scripts de prueba

└── requirements.txt
    └── Dependencias Python
```

---

# Solución de problemas comunes

## Error: falta un módulo de Python

Ejecutar nuevamente:

```bash
pip install -r requirements.txt
```

Verificar que el entorno virtual esté activo.

---

## Error: FFmpeg no encontrado

Ejecutar:

```bash
ffmpeg -version
```

Si no funciona, revisar que FFmpeg esté instalado y agregado al PATH del sistema.

---

## Error: no encuentra el archivo HRTF

Verificar que exista:

```
Codigos/hrtf.sofa
```

---

## Error de conexión entre página y backend

Verificar que:

Backend:

```
http://localhost:8000
```

Frontend:

```
http://localhost:3000
```

y que el archivo `.env` tenga:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

#  Nota final

La plataforma requiere mantener activos simultáneamente el backend y el frontend.

Si el backend está cerrado, la página web podrá abrirse, pero no podrá realizar conversiones de audio.
