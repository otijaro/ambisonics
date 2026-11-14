# Ambisonic Web Platform

Plataforma web para la conversión y reproducción de audio estéreo en formato ambisónico.

## Ejecución local

### 1. Instalar dependencias

Frontend:

```bash
pnpm install
```

Backend:

```bash
pip install -r requirements.txt
```

### 2. Configurar variables de entorno

Crear un archivo `.env` en la raíz de `Web Site` tomando como referencia `.env.example`:

```env
FRONTEND_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Iniciar el backend

En Windows puede ejecutarse:

```bash
run_backend.bat
```

### 4. Iniciar el frontend

```bash
pnpm dev
```

Abrir en el navegador:

`http://localhost:3000`

## Estado del proyecto

Esta corresponde a la versión funcional estable **v1.0**, actualmente sin integración de base de datos.

El código del frontend, backend, procesamiento DSP y los recursos necesarios para ejecutar la plataforma se encuentran incluidos en esta carpeta.
