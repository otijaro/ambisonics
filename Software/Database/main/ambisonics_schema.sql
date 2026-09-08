--
-- PostgreSQL database dump
--

\restrict CkpFEWJdvmICHCfFKa6jMiB9safn0JWLesPMk1J8PYV8gqFwL5SBMDNNprnjYh1

-- Dumped from database version 17.6
-- Dumped by pg_dump version 17.6

-- Started on 2026-08-06 16:03:38

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 220 (class 1259 OID 16402)
-- Name: audio_files; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.audio_files (
    id bigint NOT NULL,
    user_id bigint,
    original_filename character varying(255) NOT NULL,
    file_format character varying(20) NOT NULL,
    sample_rate integer,
    duration_seconds real,
    upload_path text NOT NULL,
    uploaded_at timestamp with time zone DEFAULT now(),
    session_id bigint
);


ALTER TABLE public.audio_files OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 16401)
-- Name: audio_files_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.audio_files_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.audio_files_id_seq OWNER TO postgres;

--
-- TOC entry 4908 (class 0 OID 0)
-- Dependencies: 219
-- Name: audio_files_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.audio_files_id_seq OWNED BY public.audio_files.id;


--
-- TOC entry 222 (class 1259 OID 16417)
-- Name: conversion_jobs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.conversion_jobs (
    id bigint NOT NULL,
    audio_file_id bigint,
    ambisonics_format character varying(20) DEFAULT 'ACN_SN3D'::character varying,
    status character varying(20),
    processing_time real,
    output_path text,
    error_message text,
    created_at timestamp with time zone DEFAULT now(),
    finished_at timestamp with time zone,
    session_id bigint,
    output_duration_seconds real,
    total_time_seconds real,
    dsp_time_seconds real,
    peak_memory_mb real,
    processing_mode character varying(20),
    CONSTRAINT conversion_jobs_dsp_time_check CHECK (((dsp_time_seconds IS NULL) OR (dsp_time_seconds >= (0)::double precision))),
    CONSTRAINT conversion_jobs_output_duration_check CHECK (((output_duration_seconds IS NULL) OR (output_duration_seconds >= (0)::double precision))),
    CONSTRAINT conversion_jobs_peak_memory_check CHECK (((peak_memory_mb IS NULL) OR (peak_memory_mb >= (0)::double precision))),
    CONSTRAINT conversion_jobs_processing_mode_check CHECK (((processing_mode IS NULL) OR ((processing_mode)::text = ANY ((ARRAY['memory'::character varying, 'streaming'::character varying])::text[])))),
    CONSTRAINT conversion_jobs_status_check CHECK (((status)::text = ANY ((ARRAY['pending'::character varying, 'processing'::character varying, 'completed'::character varying, 'failed'::character varying])::text[]))),
    CONSTRAINT conversion_jobs_total_time_check CHECK (((total_time_seconds IS NULL) OR (total_time_seconds >= (0)::double precision)))
);


ALTER TABLE public.conversion_jobs OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 16416)
-- Name: conversion_jobs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.conversion_jobs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.conversion_jobs_id_seq OWNER TO postgres;

--
-- TOC entry 4909 (class 0 OID 0)
-- Dependencies: 221
-- Name: conversion_jobs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.conversion_jobs_id_seq OWNED BY public.conversion_jobs.id;


--
-- TOC entry 226 (class 1259 OID 16451)
-- Name: suggestions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.suggestions (
    id bigint NOT NULL,
    session_id bigint NOT NULL,
    name character varying(100) NOT NULL,
    email character varying(255) NOT NULL,
    message text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.suggestions OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 16450)
-- Name: suggestions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.suggestions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.suggestions_id_seq OWNER TO postgres;

--
-- TOC entry 4910 (class 0 OID 0)
-- Dependencies: 225
-- Name: suggestions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.suggestions_id_seq OWNED BY public.suggestions.id;


--
-- TOC entry 218 (class 1259 OID 16390)
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id bigint NOT NULL,
    username character varying(50) NOT NULL,
    email character varying(255),
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.users OWNER TO postgres;

--
-- TOC entry 217 (class 1259 OID 16389)
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- TOC entry 4911 (class 0 OID 0)
-- Dependencies: 217
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- TOC entry 224 (class 1259 OID 16434)
-- Name: visitor_sessions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.visitor_sessions (
    id bigint NOT NULL,
    session_token uuid NOT NULL,
    entry_time timestamp with time zone DEFAULT now() NOT NULL,
    last_activity_at timestamp with time zone DEFAULT now() NOT NULL,
    exit_time timestamp with time zone,
    usage_seconds integer DEFAULT 0 NOT NULL,
    CONSTRAINT visitor_sessions_usage_seconds_check CHECK ((usage_seconds >= 0))
);


ALTER TABLE public.visitor_sessions OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 16433)
-- Name: visitor_sessions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.visitor_sessions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.visitor_sessions_id_seq OWNER TO postgres;

--
-- TOC entry 4912 (class 0 OID 0)
-- Dependencies: 223
-- Name: visitor_sessions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.visitor_sessions_id_seq OWNED BY public.visitor_sessions.id;


--
-- TOC entry 4717 (class 2604 OID 16405)
-- Name: audio_files id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audio_files ALTER COLUMN id SET DEFAULT nextval('public.audio_files_id_seq'::regclass);


--
-- TOC entry 4719 (class 2604 OID 16420)
-- Name: conversion_jobs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.conversion_jobs ALTER COLUMN id SET DEFAULT nextval('public.conversion_jobs_id_seq'::regclass);


--
-- TOC entry 4726 (class 2604 OID 16454)
-- Name: suggestions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.suggestions ALTER COLUMN id SET DEFAULT nextval('public.suggestions_id_seq'::regclass);


--
-- TOC entry 4715 (class 2604 OID 16393)
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- TOC entry 4722 (class 2604 OID 16437)
-- Name: visitor_sessions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.visitor_sessions ALTER COLUMN id SET DEFAULT nextval('public.visitor_sessions_id_seq'::regclass);


--
-- TOC entry 4742 (class 2606 OID 16410)
-- Name: audio_files audio_files_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audio_files
    ADD CONSTRAINT audio_files_pkey PRIMARY KEY (id);


--
-- TOC entry 4745 (class 2606 OID 16427)
-- Name: conversion_jobs conversion_jobs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.conversion_jobs
    ADD CONSTRAINT conversion_jobs_pkey PRIMARY KEY (id);


--
-- TOC entry 4752 (class 2606 OID 16459)
-- Name: suggestions suggestions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.suggestions
    ADD CONSTRAINT suggestions_pkey PRIMARY KEY (id);


--
-- TOC entry 4736 (class 2606 OID 16400)
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- TOC entry 4738 (class 2606 OID 16396)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- TOC entry 4740 (class 2606 OID 16398)
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- TOC entry 4748 (class 2606 OID 16443)
-- Name: visitor_sessions visitor_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.visitor_sessions
    ADD CONSTRAINT visitor_sessions_pkey PRIMARY KEY (id);


--
-- TOC entry 4750 (class 2606 OID 16445)
-- Name: visitor_sessions visitor_sessions_session_token_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.visitor_sessions
    ADD CONSTRAINT visitor_sessions_session_token_key UNIQUE (session_token);


--
-- TOC entry 4743 (class 1259 OID 16490)
-- Name: idx_audio_files_session_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audio_files_session_id ON public.audio_files USING btree (session_id);


--
-- TOC entry 4746 (class 1259 OID 16484)
-- Name: idx_conversion_jobs_session_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_conversion_jobs_session_id ON public.conversion_jobs USING btree (session_id);


--
-- TOC entry 4753 (class 2606 OID 16411)
-- Name: audio_files audio_files_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audio_files
    ADD CONSTRAINT audio_files_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- TOC entry 4755 (class 2606 OID 16428)
-- Name: conversion_jobs conversion_jobs_audio_file_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.conversion_jobs
    ADD CONSTRAINT conversion_jobs_audio_file_id_fkey FOREIGN KEY (audio_file_id) REFERENCES public.audio_files(id) ON DELETE CASCADE;


--
-- TOC entry 4756 (class 2606 OID 16474)
-- Name: conversion_jobs conversion_jobs_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.conversion_jobs
    ADD CONSTRAINT conversion_jobs_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.visitor_sessions(id) ON DELETE SET NULL;


--
-- TOC entry 4754 (class 2606 OID 16485)
-- Name: audio_files fk_audio_files_session_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audio_files
    ADD CONSTRAINT fk_audio_files_session_id FOREIGN KEY (session_id) REFERENCES public.visitor_sessions(id) ON DELETE SET NULL;


--
-- TOC entry 4757 (class 2606 OID 16460)
-- Name: suggestions suggestions_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.suggestions
    ADD CONSTRAINT suggestions_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.visitor_sessions(id);


-- Completed on 2026-08-06 16:03:38

--
-- PostgreSQL database dump complete
--

\unrestrict CkpFEWJdvmICHCfFKa6jMiB9safn0JWLesPMk1J8PYV8gqFwL5SBMDNNprnjYh1

