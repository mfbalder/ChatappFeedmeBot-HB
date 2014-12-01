--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Name: restaurantrec; Type: DATABASE; Schema: -; Owner: mfb279
--

CREATE DATABASE restaurantrec WITH TEMPLATE = template0 ENCODING = 'UTF8' LC_COLLATE = 'en_US.UTF-8' LC_CTYPE = 'en_US.UTF-8';


ALTER DATABASE restaurantrec OWNER TO mfb279;

\connect restaurantrec

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: categories; Type: TABLE; Schema: public; Owner: mfb279; Tablespace: 
--

CREATE TABLE categories (
    id integer NOT NULL,
    business_id character varying(100) NOT NULL,
    category character varying(100) NOT NULL
);


ALTER TABLE public.categories OWNER TO mfb279;

--
-- Name: categories_id_seq; Type: SEQUENCE; Schema: public; Owner: mfb279
--

CREATE SEQUENCE categories_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.categories_id_seq OWNER TO mfb279;

--
-- Name: categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mfb279
--

ALTER SEQUENCE categories_id_seq OWNED BY categories.id;


--
-- Name: categorylookup; Type: TABLE; Schema: public; Owner: mfb279; Tablespace: 
--

CREATE TABLE categorylookup (
    category character varying(100) NOT NULL,
    priority integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.categorylookup OWNER TO mfb279;

--
-- Name: neighborhoods; Type: TABLE; Schema: public; Owner: mfb279; Tablespace: 
--

CREATE TABLE neighborhoods (
    id integer NOT NULL,
    business_id character varying(100) NOT NULL,
    neighborhood character varying(100) NOT NULL
);


ALTER TABLE public.neighborhoods OWNER TO mfb279;

--
-- Name: neighborhoods_id_seq; Type: SEQUENCE; Schema: public; Owner: mfb279
--

CREATE SEQUENCE neighborhoods_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.neighborhoods_id_seq OWNER TO mfb279;

--
-- Name: neighborhoods_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mfb279
--

ALTER SEQUENCE neighborhoods_id_seq OWNED BY neighborhoods.id;


--
-- Name: ratings; Type: TABLE; Schema: public; Owner: mfb279; Tablespace: 
--

CREATE TABLE ratings (
    id character varying(100) NOT NULL,
    user_id character varying(100) NOT NULL,
    business_id character varying(100) NOT NULL,
    review_text text,
    stars double precision,
    useful_votes double precision
);


ALTER TABLE public.ratings OWNER TO mfb279;

--
-- Name: restaurants; Type: TABLE; Schema: public; Owner: mfb279; Tablespace: 
--

CREATE TABLE restaurants (
    id character varying(120) NOT NULL,
    name character varying(120) NOT NULL,
    divey boolean,
    vegan boolean,
    happy_hour boolean,
    open_thurs timestamp without time zone,
    counter boolean,
    byob boolean,
    open_fri timestamp without time zone,
    latitude double precision,
    outdoor_seating boolean,
    alcohol boolean,
    classy boolean,
    mastercard boolean,
    parking_lot boolean,
    touristy boolean,
    corkage boolean,
    open_tues timestamp without time zone,
    brunch boolean,
    amex boolean,
    open_mon timestamp without time zone,
    waiter boolean,
    parking_street boolean,
    hipster boolean,
    live_music boolean,
    dairy_free boolean,
    background_music boolean,
    price_range integer,
    breakfast boolean,
    parking_garage boolean,
    state character varying(5),
    credit_cards boolean,
    close_fri timestamp without time zone,
    lunch boolean,
    kids boolean,
    parking_valet boolean,
    takeout boolean,
    address character varying(120),
    close_thurs timestamp without time zone,
    cash_only boolean,
    dessert boolean,
    halal boolean,
    reservations boolean,
    open_sat timestamp without time zone,
    trendy boolean,
    delivery boolean,
    close_wed timestamp without time zone,
    wifi character varying(10),
    city character varying(64),
    discover boolean,
    wheelchair boolean,
    gluten_free boolean,
    stars double precision,
    visa boolean,
    intimate boolean,
    latenight boolean,
    dinner boolean,
    coat_check boolean,
    longitude double precision,
    close_mon timestamp without time zone,
    close_tues timestamp without time zone,
    close_sat timestamp without time zone,
    open_sun timestamp without time zone,
    soy_free boolean,
    close_sun timestamp without time zone,
    casual boolean,
    kosher boolean,
    drive_thru boolean,
    vegetarian boolean,
    open_wed timestamp without time zone,
    noise_level character varying(10),
    groups boolean,
    twenty_four boolean,
    romantic boolean,
    upscale boolean
);


ALTER TABLE public.restaurants OWNER TO mfb279;

--
-- Name: users; Type: TABLE; Schema: public; Owner: mfb279; Tablespace: 
--

CREATE TABLE users (
    id character varying(100) NOT NULL,
    email character varying(64),
    password character varying(64),
    name character varying(64),
    average_rating double precision
);


ALTER TABLE public.users OWNER TO mfb279;

--
-- Name: id; Type: DEFAULT; Schema: public; Owner: mfb279
--

ALTER TABLE ONLY categories ALTER COLUMN id SET DEFAULT nextval('categories_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: mfb279
--

ALTER TABLE ONLY neighborhoods ALTER COLUMN id SET DEFAULT nextval('neighborhoods_id_seq'::regclass);


--
-- Name: categories_pkey; Type: CONSTRAINT; Schema: public; Owner: mfb279; Tablespace: 
--

ALTER TABLE ONLY categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (id);


--
-- Name: categorylookup_pkey; Type: CONSTRAINT; Schema: public; Owner: mfb279; Tablespace: 
--

ALTER TABLE ONLY categorylookup
    ADD CONSTRAINT categorylookup_pkey PRIMARY KEY (category);


--
-- Name: neighborhoods_pkey; Type: CONSTRAINT; Schema: public; Owner: mfb279; Tablespace: 
--

ALTER TABLE ONLY neighborhoods
    ADD CONSTRAINT neighborhoods_pkey PRIMARY KEY (id);


--
-- Name: ratings_pkey; Type: CONSTRAINT; Schema: public; Owner: mfb279; Tablespace: 
--

ALTER TABLE ONLY ratings
    ADD CONSTRAINT ratings_pkey PRIMARY KEY (id);


--
-- Name: restaurants_pkey; Type: CONSTRAINT; Schema: public; Owner: mfb279; Tablespace: 
--

ALTER TABLE ONLY restaurants
    ADD CONSTRAINT restaurants_pkey PRIMARY KEY (id);


--
-- Name: users_pkey; Type: CONSTRAINT; Schema: public; Owner: mfb279; Tablespace: 
--

ALTER TABLE ONLY users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: categories_business_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mfb279
--

ALTER TABLE ONLY categories
    ADD CONSTRAINT categories_business_id_fkey FOREIGN KEY (business_id) REFERENCES restaurants(id);


--
-- Name: neighborhoods_business_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mfb279
--

ALTER TABLE ONLY neighborhoods
    ADD CONSTRAINT neighborhoods_business_id_fkey FOREIGN KEY (business_id) REFERENCES restaurants(id);


--
-- Name: ratings_business_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mfb279
--

ALTER TABLE ONLY ratings
    ADD CONSTRAINT ratings_business_id_fkey FOREIGN KEY (business_id) REFERENCES restaurants(id);


--
-- Name: ratings_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mfb279
--

ALTER TABLE ONLY ratings
    ADD CONSTRAINT ratings_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id);


--
-- Name: public; Type: ACL; Schema: -; Owner: mfb279
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM mfb279;
GRANT ALL ON SCHEMA public TO mfb279;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

