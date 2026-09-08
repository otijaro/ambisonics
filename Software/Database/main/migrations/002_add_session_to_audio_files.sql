BEGIN;

-- Añade la sesión que originó la carga del audio.
-- Se permite NULL para conservar los registros antiguos
-- y admitir posteriormente audios asociados a usuarios registrados.
ALTER TABLE public.audio_files
ADD COLUMN IF NOT EXISTS session_id BIGINT;

-- Crea la relación entre el audio y la sesión visitante.
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'fk_audio_files_session_id'
    ) THEN
        ALTER TABLE public.audio_files
        ADD CONSTRAINT fk_audio_files_session_id
        FOREIGN KEY (session_id)
        REFERENCES public.visitor_sessions(id)
        ON DELETE SET NULL;
    END IF;
END
$$;

-- Mejora la velocidad de las búsquedas de audios por sesión.
CREATE INDEX IF NOT EXISTS idx_audio_files_session_id
ON public.audio_files(session_id);

COMMIT;