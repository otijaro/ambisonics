--
-- PostgreSQL schema-only (sin datos, sin dueños ni privilegios)
-- Esquema 'public' de la base Neon 'neondb' (servidor PostgreSQL 18.7)
--

SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

CREATE SEQUENCE public.processing_requests_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

CREATE SEQUENCE public.suggestions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

CREATE SEQUENCE public.temporary_files_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

CREATE SEQUENCE public.user_sessions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

CREATE SEQUENCE public.users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

CREATE TABLE public.processing_requests (
    id bigint DEFAULT nextval('public.processing_requests_id_seq'::regclass) NOT NULL,
    original_filename text NOT NULL,
    input_mode character varying(20) NOT NULL,
    status character varying(20) DEFAULT 'processing'::character varying NOT NULL,
    processing_sample_rate_hz integer,
    original_duration_seconds double precision,
    processing_seconds double precision,
    processing_percentage double precision,
    requested_at timestamp with time zone DEFAULT now() NOT NULL,
    finished_at timestamp with time zone,
    error_message text,
    user_id bigint,
    input_sample_rate_hz integer,
    CONSTRAINT processing_requests_input_mode_check CHECK (((input_mode)::text = ANY ((ARRAY['stereo'::character varying, 'tetra_4mic'::character varying])::text[]))),
    CONSTRAINT processing_requests_original_duration_check CHECK (((original_duration_seconds IS NULL) OR (original_duration_seconds >= (0)::double precision))),
    CONSTRAINT processing_requests_processing_percentage_check CHECK (((processing_percentage IS NULL) OR (processing_percentage >= (0)::double precision))),
    CONSTRAINT processing_requests_processing_seconds_check CHECK (((processing_seconds IS NULL) OR (processing_seconds >= (0)::double precision))),
    CONSTRAINT processing_requests_sample_rate_check CHECK (((processing_sample_rate_hz IS NULL) OR (processing_sample_rate_hz > 0))),
    CONSTRAINT processing_requests_status_check CHECK (((status)::text = ANY ((ARRAY['processing'::character varying, 'completed'::character varying, 'failed'::character varying])::text[])))
);

CREATE TABLE public.suggestions (
    id bigint DEFAULT nextval('public.suggestions_id_seq'::regclass) NOT NULL,
    name character varying(120),
    email character varying(254),
    message text NOT NULL,
    consent_given boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT suggestions_privacy_check CHECK ((((name IS NULL) AND (email IS NULL)) OR (consent_given = true)))
);

CREATE TABLE public.temporary_files (
    id bigint DEFAULT nextval('public.temporary_files_id_seq'::regclass) NOT NULL,
    processing_request_id bigint NOT NULL,
    file_type character varying(30) NOT NULL,
    storage_path text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    expires_at timestamp with time zone DEFAULT (now() + '24:00:00'::interval) NOT NULL,
    deleted_at timestamp with time zone,
    CONSTRAINT temporary_files_expiration_check CHECK ((expires_at > created_at))
);

CREATE TABLE public.user_sessions (
    id bigint DEFAULT nextval('public.user_sessions_id_seq'::regclass) NOT NULL,
    user_id bigint NOT NULL,
    token_hash text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    last_activity_at timestamp with time zone DEFAULT now() NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    revoked_at timestamp with time zone,
    CONSTRAINT user_sessions_expiration_check CHECK ((expires_at > created_at))
);

CREATE TABLE public.users (
    id bigint DEFAULT nextval('public.users_id_seq'::regclass) NOT NULL,
    name character varying(120) NOT NULL,
    email character varying(254) NOT NULL,
    password_hash text NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    consent_given boolean DEFAULT false NOT NULL,
    consent_at timestamp with time zone,
    recovery_code_hash character varying(255),
    CONSTRAINT users_consent_check CHECK ((((consent_given = true) AND (consent_at IS NOT NULL)) OR ((consent_given = false) AND (consent_at IS NULL))))
);

ALTER SEQUENCE public.processing_requests_id_seq OWNED BY public.processing_requests.id;

ALTER SEQUENCE public.suggestions_id_seq OWNED BY public.suggestions.id;

ALTER SEQUENCE public.temporary_files_id_seq OWNED BY public.temporary_files.id;

ALTER SEQUENCE public.user_sessions_id_seq OWNED BY public.user_sessions.id;

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;

ALTER TABLE ONLY public.processing_requests
    ADD CONSTRAINT processing_requests_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.suggestions
    ADD CONSTRAINT suggestions_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.temporary_files
    ADD CONSTRAINT temporary_files_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.user_sessions
    ADD CONSTRAINT user_sessions_token_hash_key UNIQUE (token_hash);

ALTER TABLE ONLY public.user_sessions
    ADD CONSTRAINT user_sessions_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);

CREATE INDEX idx_processing_requests_requested_at ON public.processing_requests USING btree (requested_at);

CREATE INDEX idx_processing_requests_status ON public.processing_requests USING btree (status);

CREATE INDEX idx_processing_requests_user_id ON public.processing_requests USING btree (user_id);

CREATE INDEX idx_suggestions_created_at ON public.suggestions USING btree (created_at);

CREATE INDEX idx_temporary_files_expires_at ON public.temporary_files USING btree (expires_at);

CREATE INDEX idx_temporary_files_processing_request_id ON public.temporary_files USING btree (processing_request_id);

CREATE INDEX idx_user_sessions_expires_at ON public.user_sessions USING btree (expires_at);

CREATE INDEX idx_user_sessions_user_id ON public.user_sessions USING btree (user_id);

CREATE UNIQUE INDEX idx_users_email_unique ON public.users USING btree (lower((email)::text));

ALTER TABLE ONLY public.processing_requests
    ADD CONSTRAINT processing_requests_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE SET NULL;

ALTER TABLE ONLY public.temporary_files
    ADD CONSTRAINT temporary_files_processing_request_id_fkey FOREIGN KEY (processing_request_id) REFERENCES public.processing_requests(id) ON DELETE CASCADE;

ALTER TABLE ONLY public.user_sessions
    ADD CONSTRAINT user_sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;
