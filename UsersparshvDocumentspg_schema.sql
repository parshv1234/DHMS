--
-- PostgreSQL database dump
--

-- Dumped from database version 14.13 (Homebrew)
-- Dumped by pg_dump version 14.13 (Homebrew)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
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
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: dhms_user
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO dhms_user;

--
-- Name: appointment_record; Type: TABLE; Schema: public; Owner: dhms_user
--

CREATE TABLE public.appointment_record (
    id character varying(36) NOT NULL,
    patient_id character varying NOT NULL,
    doctor_id character varying NOT NULL,
    appointment_date date NOT NULL,
    appointment_time time without time zone NOT NULL,
    reason character varying(255),
    status character varying(50) DEFAULT 'Pending'::text NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    notes text
);


ALTER TABLE public.appointment_record OWNER TO dhms_user;

--
-- Name: appointment_record_id_seq; Type: SEQUENCE; Schema: public; Owner: dhms_user
--

CREATE SEQUENCE public.appointment_record_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.appointment_record_id_seq OWNER TO dhms_user;

--
-- Name: appointment_record_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dhms_user
--

ALTER SEQUENCE public.appointment_record_id_seq OWNED BY public.appointment_record.id;


--
-- Name: department; Type: TABLE; Schema: public; Owner: dhms_user
--

CREATE TABLE public.department (
    id character varying(20) NOT NULL,
    name character varying(100) NOT NULL,
    description character varying(500),
    head_doctor_id character varying(20),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.department OWNER TO dhms_user;

--
-- Name: doctor_record; Type: TABLE; Schema: public; Owner: dhms_user
--

CREATE TABLE public.doctor_record (
    id character varying(20) NOT NULL,
    name character varying(100) NOT NULL,
    age integer NOT NULL,
    gender character varying(10) NOT NULL,
    date_of_birth character varying(10) NOT NULL,
    blood_group character varying(5) NOT NULL,
    department_id character varying(20) NOT NULL,
    department_name character varying(100) NOT NULL,
    contact_number_1 character varying(15) NOT NULL,
    contact_number_2 character varying(15),
    aadhar_or_voter_id character varying(20) NOT NULL,
    email_id character varying(100) NOT NULL,
    qualification character varying(100) NOT NULL,
    specialisation character varying(100) NOT NULL,
    years_of_experience integer NOT NULL,
    address character varying(200) NOT NULL,
    city character varying(50) NOT NULL,
    state character varying(50) NOT NULL,
    pin_code character varying(10) NOT NULL,
    password character varying(255) NOT NULL,
    last_login timestamp without time zone,
    role character varying(50) DEFAULT 'doctor'::character varying NOT NULL
);


ALTER TABLE public.doctor_record OWNER TO dhms_user;

--
-- Name: patient_record; Type: TABLE; Schema: public; Owner: dhms_user
--

CREATE TABLE public.patient_record (
    id character varying(36) NOT NULL,
    name character varying(100) NOT NULL,
    age integer NOT NULL,
    gender character varying(10) NOT NULL,
    contact_number_1 character varying(20) NOT NULL,
    contact_number_2 character varying(20),
    address character varying(250),
    next_of_kin_name character varying(100) NOT NULL,
    next_of_kin_relation_to_patient character varying(50) NOT NULL,
    next_of_kin_contact_number character varying(20) NOT NULL,
    email_id character varying(100) NOT NULL,
    qr_code_path character varying(250) NOT NULL
);


ALTER TABLE public.patient_record OWNER TO dhms_user;

--
-- Name: payments; Type: TABLE; Schema: public; Owner: dhms_user
--

CREATE TABLE public.payments (
    id character varying(36) NOT NULL,
    patient_id character varying NOT NULL,
    doctor_id character varying NOT NULL,
    amount double precision NOT NULL,
    admin_share double precision NOT NULL,
    doctor_share double precision NOT NULL,
    payment_status character varying(20) DEFAULT 'Pending'::character varying,
    payment_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.payments OWNER TO dhms_user;

--
-- Name: users; Type: TABLE; Schema: public; Owner: dhms_user
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(100) NOT NULL,
    email character varying(255) NOT NULL,
    phone character varying(15),
    password character varying(255) NOT NULL,
    otp character varying(6),
    otp_expiry timestamp without time zone,
    is_verified boolean DEFAULT false,
    role character varying(20) NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.users OWNER TO dhms_user;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: dhms_user
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO dhms_user;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dhms_user
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: appointment_record id; Type: DEFAULT; Schema: public; Owner: dhms_user
--

ALTER TABLE ONLY public.appointment_record ALTER COLUMN id SET DEFAULT nextval('public.appointment_record_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: dhms_user
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: dhms_user
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: appointment_record appointment_record_id_key; Type: CONSTRAINT; Schema: public; Owner: dhms_user
--

ALTER TABLE ONLY public.appointment_record
    ADD CONSTRAINT appointment_record_id_key UNIQUE (id);


--
-- Name: appointment_record appointment_record_pkey; Type: CONSTRAINT; Schema: public; Owner: dhms_user
--

ALTER TABLE ONLY public.appointment_record
    ADD CONSTRAINT appointment_record_pkey PRIMARY KEY (id);


--
-- Name: department department_name_key; Type: CONSTRAINT; Schema: public; Owner: dhms_user
--

ALTER TABLE ONLY public.department
    ADD CONSTRAINT department_name_key UNIQUE (name);


--
-- Name: department department_pkey; Type: CONSTRAINT; Schema: public; Owner: dhms_user
--

ALTER TABLE ONLY public.department
    ADD CONSTRAINT department_pkey PRIMARY KEY (id);


--
-- Name: doctor_record doctor_record_email_id_key; Type: CONSTRAINT; Schema: public; Owner: dhms_user
--

ALTER TABLE ONLY public.doctor_record
    ADD CONSTRAINT doctor_record_email_id_key UNIQUE (email_id);


--
-- Name: patient_record idx_16386_sqlite_autoindex_patient_record_1; Type: CONSTRAINT; Schema: public; Owner: dhms_user
--

ALTER TABLE ONLY public.patient_record
    ADD CONSTRAINT idx_16386_sqlite_autoindex_patient_record_1 PRIMARY KEY (id);


--
-- Name: doctor_record idx_16391_sqlite_autoindex_doctor_record_1; Type: CONSTRAINT; Schema: public; Owner: dhms_user
--

ALTER TABLE ONLY public.doctor_record
    ADD CONSTRAINT idx_16391_sqlite_autoindex_doctor_record_1 PRIMARY KEY (id);


--
-- Name: patient_record patient_record_id_key; Type: CONSTRAINT; Schema: public; Owner: dhms_user
--

ALTER TABLE ONLY public.patient_record
    ADD CONSTRAINT patient_record_id_key UNIQUE (id);


--
-- Name: payments payments_pkey; Type: CONSTRAINT; Schema: public; Owner: dhms_user
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_pkey PRIMARY KEY (id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: dhms_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_phone_key; Type: CONSTRAINT; Schema: public; Owner: dhms_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_phone_key UNIQUE (phone);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: dhms_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: appointment_record appointment_record_doctor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dhms_user
--

ALTER TABLE ONLY public.appointment_record
    ADD CONSTRAINT appointment_record_doctor_id_fkey FOREIGN KEY (doctor_id) REFERENCES public.doctor_record(id) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: appointment_record appointment_record_patient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dhms_user
--

ALTER TABLE ONLY public.appointment_record
    ADD CONSTRAINT appointment_record_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES public.patient_record(id) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: department department_head_doctor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dhms_user
--

ALTER TABLE ONLY public.department
    ADD CONSTRAINT department_head_doctor_id_fkey FOREIGN KEY (head_doctor_id) REFERENCES public.doctor_record(id);


--
-- Name: payments fk_doctor; Type: FK CONSTRAINT; Schema: public; Owner: dhms_user
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT fk_doctor FOREIGN KEY (doctor_id) REFERENCES public.doctor_record(id) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: doctor_record fk_doctor_department; Type: FK CONSTRAINT; Schema: public; Owner: dhms_user
--

ALTER TABLE ONLY public.doctor_record
    ADD CONSTRAINT fk_doctor_department FOREIGN KEY (department_id) REFERENCES public.department(id);


--
-- Name: payments fk_patient; Type: FK CONSTRAINT; Schema: public; Owner: dhms_user
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT fk_patient FOREIGN KEY (patient_id) REFERENCES public.patient_record(id) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: parshv
--

GRANT USAGE ON SCHEMA public TO dhms_user;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: public; Owner: parshv
--

ALTER DEFAULT PRIVILEGES FOR ROLE parshv IN SCHEMA public GRANT ALL ON TABLES  TO dhms_user;


--
-- PostgreSQL database dump complete
--

