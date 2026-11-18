# Database v2.0

Esquema oficial limpio de la base de datos de la plataforma Ambisonics, tomado de **Neon PostgreSQL** (base `neondb`, esquema `public`, servidor PostgreSQL 18.7).

- **Archivo:** `ambisonics_schema_v2.sql` (solo estructura: secuencias, tablas, restricciones, índices y llaves foráneas).
- **Tablas (5):** `users`, `user_sessions`, `processing_requests`, `temporary_files`, `suggestions`.
- **Datos:** 0 registros de prueba en las 5 tablas.
- **Secuencias:** sin uso, en su valor inicial; el primer `id` generado en cada tabla es 1.
- **Sin dueños ni privilegios:** el script no contiene `OWNER TO`, `GRANT` ni credenciales.

## Relaciones

```text
users 1 ──< user_sessions            (ON DELETE CASCADE)
users 1 ──< processing_requests      (ON DELETE SET NULL)
processing_requests 1 ──< temporary_files   (ON DELETE CASCADE)
suggestions                           (independiente)
```

## Crear la base desde cero

```bash
psql "$DATABASE_URL" -f ambisonics_schema_v2.sql
```

`DATABASE_URL` debe definirse como variable de entorno, nunca dentro de este repositorio. Para ejecutarlo, el backend lee la variable desde su archivo `.env` (que no se versiona).

## Notas

- El esquema se extrajo con una consulta al catálogo de PostgreSQL, equivalente a `pg_dump --schema-only --no-owner --no-privileges`.
- La versión anterior del esquema (visitor sessions, `audio_files`, `conversion_jobs`) está en `../Database_v1.0/`.