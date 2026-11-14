# 08. Configuración y Despliegue (Deployment)

Esta guía expone el paso a paso necesario para levantar el proyecto Ambisonic localmente y para llevar el código fuente a entornos productivos de servidor utilizando plataformas *Platform as a Service (PaaS)*. 
Como se trata de una arquitectura desacoplada, Frontend (Node.js) y Backend (Python) deben ser ejecutados y desplegados de manera separada.

## 1. Ejecución Local desde Cero

### 1.1 Clonar Repositorio
```bash
git clone <tu-repositorio>
cd ambisonic
```

### 1.2 Ejecución del Backend API (FastAPI)
Requiere **Python 3.10+**.
1. Abrir terminal, moverse a la raíz del repositorio y crear el entorno virtual:
   ```bash
   python -m venv venv
   # Activar en Windows: venv\Scripts\activate
   # Activar en Mac/Linux: source venv/bin/activate
   ```
2. Instalar dependencias necesarias:
   ```bash
   pip install -r requirements.txt
   ```
3. Ejecutar el servidor con Uvicorn de forma local (asegúrate de incluir el path como módulo):
   ```bash
   uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
   ```
4. Comprobación: Visita `http://localhost:8000/api/health`. Debería retornar `{"status": "healthy"}`.

### 1.3 Ejecución del Frontend (Next.js)
Requiere **Node.js 18+** y un gestor de paquetes (`npm` o `pnpm`).
1. Abrir una **nueva** terminal en la raíz del proyecto.
2. Definir que el frontend apunte a tu servidor local. Edita o crea el archivo `.env.local` en la raíz con la siguiente línea:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```
3. Instalar los paquetes JS y arrancar:
   ```bash
   npm install
   npm run dev
   ```
4. Comprobación: Entra a `http://localhost:3000`. Deberías ver la landing y poder realizar conversiones exitosas.

---

## 2. Despliegue Productivo

### 2.1 Backend en Railway (Recomendado)
El proyecto contiene configuraciones para Nixpacks (`nixpacks.toml`) y Procfile, lo que facilita el despliegue automático en Railway / Heroku.
- Se debe asegurar que las dependencias de sistema de Linux instalen `libsndfile1` y `ffmpeg` para que los módulos `soundfile` y `subprocess` operen. Esto está parametrizado implícitamente a nivel `nixpacks.toml`.
- **Proceso:**
  1. Conectar Railway a tu repositorio GitHub.
  2. Apuntar el root directory a la raíz del proyecto.
  3. Ejecutar comando de arranque en Railway (usualmente se sobreescribe automático con el `Procfile`): 
     `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
  4. Obtener URL de dominio autogenerada por Railway (ej. `https://api-ambisonic.up.railway.app`).

### 2.2 Frontend en Vercel
1. Conectar Vercel con el repositorio de GitHub de Ambisonic.
2. Vercel detectará el *framework preset* "Next.js".
3. **Paso crítico (Environment Variables):** Configurar en Vercel la variable `NEXT_PUBLIC_API_URL` apuntando al dominio otorgado por Railway:
   `NEXT_PUBLIC_API_URL = https://api-ambisonic.up.railway.app`
4. Deploy.

---

## 3. Errores Comunes y Soluciones

**Error:** `RuntimeError: Error opening <file>. Format not recognised.` al ejecutar conversiones en backend.
**Solución:** Probablemente `libsndfile` o ffmpeg falten en el servidor Linux de producción (Railway). Revisa el setup de *apt-get* en los build commands o Dockerfile.

**Error:** `CORS Failed` o Network Error en el formulario del Frontend.
**Solución:** Dos posibilidades:
- En producción: Olvidaste agregar el dominio frontend (`https://ambisonic.vercel.app`) a la lista `allow_origins` de CORS dentro de `backend/main.py`.
- En local: `NEXT_PUBLIC_API_URL` no fue definido o está apuntando a un puerto erróneo.

**Error:** El visualizador 3D no carga o crashea la página.
**Solución:** Verifica las dependencias exactas en el `package.json` de React Three Fiber y Drei. Las versiones mayores suelen romper APIs de geometría.

**Nota:** Es crucial que el archivo `hrtf.sofa` (3MB) esté alojado obligatoriamente en el sistema de archivos junto a `main.py` antes de intentar inicializar FastAPI, o el modo 3D binaural renderizará un fallback degradado y se generarán alertas en los *Logs*.
