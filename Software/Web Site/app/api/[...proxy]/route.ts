import { NextRequest } from 'next/server';

export const maxDuration = 300; // 5 minutos de timeout para conversiones pesadas

async function handleRequest(req: NextRequest) {
  // Construir la URL destino en FastAPI (ej. /api/convert)
  const path = req.nextUrl.pathname;
  const searchParams = req.nextUrl.search;
  const backendUrl = `http://127.0.0.1:8000${path}${searchParams}`;

  // Clonar los headers, pero modificar el host
  const headers = new Headers(req.headers);
  headers.set('host', '127.0.0.1:8000');
  
  // Evitar conflictos con Next.js encoding
  headers.delete('accept-encoding');

  const options: RequestInit = {
    method: req.method,
    headers: headers,
  };

  if (req.method !== 'GET' && req.method !== 'HEAD' && req.body) {
    options.body = req.body;
    // @ts-ignore
    options.duplex = 'half';
  }

  try {
    const res = await fetch(backendUrl, options);
    
    // Clonamos la respuesta para devolverla al cliente
    return new Response(res.body, {
      status: res.status,
      headers: res.headers,
    });
  } catch (error) {
    console.error("Error en proxy de Next.js hacia FastAPI:", error);
    return new Response(JSON.stringify({ detail: "Error de conexión con el backend interno." }), {
      status: 502,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

export async function GET(req: NextRequest) {
  return handleRequest(req);
}

export async function POST(req: NextRequest) {
  return handleRequest(req);
}

export async function PUT(req: NextRequest) {
  return handleRequest(req);
}

export async function DELETE(req: NextRequest) {
  return handleRequest(req);
}
