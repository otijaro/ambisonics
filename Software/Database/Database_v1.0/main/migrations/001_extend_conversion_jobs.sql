BEGIN;

-- Relación entre una conversión y la sesión del visitante.
ALTER TABLE public.conversion_jobs
    ADD COLUMN IF NOT EXISTS session_id BIGINT;

-- Métricas generadas durante el procesamiento.
ALTER TABLE public.conversion_jobs
    ADD COLUMN IF NOT EXISTS output_duration_seconds REAL,
    ADD COLUMN IF NOT EXISTS total_time_seconds REAL,
    ADD COLUMN IF NOT EXISTS dsp_time_seconds REAL,
    ADD COLUMN IF NOT EXISTS peak_memory_mb REAL,
    ADD COLUMN IF NOT EXISTS processing_mode VARCHAR(20);


-- Llave foránea: conversion_jobs.session_id
-- referencia visitor_sessions.id.
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'conversion_jobs_session_id_fkey'
          AND conrelid = 'public.conversion_jobs'::regclass
    ) THEN
        ALTER TABLE public.conversion_jobs
            ADD CONSTRAINT conversion_jobs_session_id_fkey
            FOREIGN KEY (session_id)
            REFERENCES public.visitor_sessions(id)
            ON DELETE SET NULL;
    END IF;
END
$$;


-- Las duraciones y tiempos no pueden ser negativos.
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'conversion_jobs_output_duration_check'
          AND conrelid = 'public.conversion_jobs'::regclass
    ) THEN
        ALTER TABLE public.conversion_jobs
            ADD CONSTRAINT conversion_jobs_output_duration_check
            CHECK (
                output_duration_seconds IS NULL
                OR output_duration_seconds >= 0
            );
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'conversion_jobs_total_time_check'
          AND conrelid = 'public.conversion_jobs'::regclass
    ) THEN
        ALTER TABLE public.conversion_jobs
            ADD CONSTRAINT conversion_jobs_total_time_check
            CHECK (
                total_time_seconds IS NULL
                OR total_time_seconds >= 0
            );
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'conversion_jobs_dsp_time_check'
          AND conrelid = 'public.conversion_jobs'::regclass
    ) THEN
        ALTER TABLE public.conversion_jobs
            ADD CONSTRAINT conversion_jobs_dsp_time_check
            CHECK (
                dsp_time_seconds IS NULL
                OR dsp_time_seconds >= 0
            );
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'conversion_jobs_peak_memory_check'
          AND conrelid = 'public.conversion_jobs'::regclass
    ) THEN
        ALTER TABLE public.conversion_jobs
            ADD CONSTRAINT conversion_jobs_peak_memory_check
            CHECK (
                peak_memory_mb IS NULL
                OR peak_memory_mb >= 0
            );
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'conversion_jobs_processing_mode_check'
          AND conrelid = 'public.conversion_jobs'::regclass
    ) THEN
        ALTER TABLE public.conversion_jobs
            ADD CONSTRAINT conversion_jobs_processing_mode_check
            CHECK (
                processing_mode IS NULL
                OR processing_mode IN ('memory', 'streaming')
            );
    END IF;
END
$$;


-- Facilita búsquedas de conversiones por sesión.
CREATE INDEX IF NOT EXISTS idx_conversion_jobs_session_id
    ON public.conversion_jobs(session_id);

COMMIT;