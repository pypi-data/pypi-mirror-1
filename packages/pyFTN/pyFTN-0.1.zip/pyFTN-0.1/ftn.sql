
CREATE TABLE messages (
-- source	address, name
-- destination	address, name
-- recvfrom	authorized deliverer, deliverer info
-- sendto       requred auth,


    id character varying NOT NULL,
    body bytea,
    info character varying,
    injector character varying,
    injected date
);



CREATE TABLE areas (
    name character varying NOT NULL,
    hold_delay integer,
    flush_delay integer
);


--
-- TOC entry 6 (OID 17169)
-- Name: message; Type: TABLE; Schema: public; Owner: root
--



--
-- TOC entry 7 (OID 17218)
-- Name: msgfiles; Type: TABLE; Schema: public; Owner: root
--

CREATE TABLE msgfiles (
    diskname character varying NOT NULL,
    msg integer,
    name character varying
);


--
-- TOC entry 8 (OID 17260)
-- Name: msg_area; Type: TABLE; Schema: public; Owner: root
--

CREATE TABLE msg_area (
    msg integer,
    area character varying
);


--
-- TOC entry 9 (OID 17273)
-- Name: address; Type: TABLE; Schema: public; Owner: root
--

CREATE TABLE address (
    ftna character(20) NOT NULL
);


--
-- TOC entry 10 (OID 17277)
-- Name: deliver; Type: TABLE; Schema: public; Owner: root
--

CREATE TABLE deliver (
    msg integer,
    ftna character(20)
);


--
-- TOC entry 11 (OID 17287)
-- Name: seenby; Type: TABLE; Schema: public; Owner: root
--

CREATE TABLE seenby (
    msg integer,
    ftna character(20)
);


--
-- TOC entry 12 (OID 17297)
-- Name: subscribe; Type: TABLE; Schema: public; Owner: root
--

CREATE TABLE subscribe (
    ftna character(20),
    area character varying
);


--
-- Data for TOC entry 18 (OID 17162)
-- Name: areas; Type: TABLE DATA; Schema: public; Owner: root
--

COPY areas (name, hold_delay, flush_delay) FROM stdin;
fluid.local	\N	\N
\.


--
-- Data for TOC entry 19 (OID 17169)
-- Name: message; Type: TABLE DATA; Schema: public; Owner: root
--

COPY message (id, body, info, injector, injected) FROM stdin;
\.


--
-- Data for TOC entry 20 (OID 17218)
-- Name: msgfiles; Type: TABLE DATA; Schema: public; Owner: root
--

COPY msgfiles (diskname, msg, name) FROM stdin;
\.


--
-- Data for TOC entry 21 (OID 17260)
-- Name: msg_area; Type: TABLE DATA; Schema: public; Owner: root
--

COPY msg_area (msg, area) FROM stdin;
\.


--
-- Data for TOC entry 22 (OID 17273)
-- Name: address; Type: TABLE DATA; Schema: public; Owner: root
--

COPY address (ftna) FROM stdin;
2:5020/12000        
\.


--
-- Data for TOC entry 23 (OID 17277)
-- Name: deliver; Type: TABLE DATA; Schema: public; Owner: root
--

COPY deliver (msg, ftna) FROM stdin;
\.


--
-- Data for TOC entry 24 (OID 17287)
-- Name: seenby; Type: TABLE DATA; Schema: public; Owner: root
--

COPY seenby (msg, ftna) FROM stdin;
\.


--
-- Data for TOC entry 25 (OID 17297)
-- Name: subscribe; Type: TABLE DATA; Schema: public; Owner: root
--

COPY subscribe (ftna, area) FROM stdin;
2:5020/12000        	fluid.local
\.


--
-- TOC entry 17 (OID 17362)
-- Name: subscribe_idx; Type: INDEX; Schema: public; Owner: root
--

CREATE UNIQUE INDEX subscribe_idx ON subscribe USING btree (area, ftna);


--
-- TOC entry 13 (OID 17167)
-- Name: areas_pkey; Type: CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY areas
    ADD CONSTRAINT areas_pkey PRIMARY KEY (name);


--
-- TOC entry 14 (OID 17174)
-- Name: message_pkey; Type: CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY message
    ADD CONSTRAINT message_pkey PRIMARY KEY (id);


--
-- TOC entry 15 (OID 17223)
-- Name: msgfiles_pkey; Type: CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY msgfiles
    ADD CONSTRAINT msgfiles_pkey PRIMARY KEY (diskname);


--
-- TOC entry 16 (OID 17275)
-- Name: address_pkey; Type: CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY address
    ADD CONSTRAINT address_pkey PRIMARY KEY (ftna);


--
-- TOC entry 26 (OID 17225)
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY msgfiles
    ADD CONSTRAINT "$1" FOREIGN KEY (msg) REFERENCES message(id);


--
-- TOC entry 27 (OID 17265)
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY msg_area
    ADD CONSTRAINT "$1" FOREIGN KEY (msg) REFERENCES message(id);


--
-- TOC entry 28 (OID 17269)
-- Name: $2; Type: FK CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY msg_area
    ADD CONSTRAINT "$2" FOREIGN KEY (area) REFERENCES areas(name);


--
-- TOC entry 29 (OID 17279)
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY deliver
    ADD CONSTRAINT "$1" FOREIGN KEY (msg) REFERENCES message(id);


--
-- TOC entry 30 (OID 17283)
-- Name: $2; Type: FK CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY deliver
    ADD CONSTRAINT "$2" FOREIGN KEY (ftna) REFERENCES address(ftna);


--
-- TOC entry 31 (OID 17289)
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY seenby
    ADD CONSTRAINT "$1" FOREIGN KEY (msg) REFERENCES message(id);


--
-- TOC entry 32 (OID 17293)
-- Name: $2; Type: FK CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY seenby
    ADD CONSTRAINT "$2" FOREIGN KEY (ftna) REFERENCES address(ftna);


--
-- TOC entry 33 (OID 17302)
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY subscribe
    ADD CONSTRAINT "$1" FOREIGN KEY (ftna) REFERENCES address(ftna);


--
-- TOC entry 34 (OID 17306)
-- Name: $2; Type: FK CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY subscribe
    ADD CONSTRAINT "$2" FOREIGN KEY (area) REFERENCES areas(name);


SET SESSION AUTHORIZATION 'postgres';

--
-- TOC entry 3 (OID 2200)
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON SCHEMA public IS 'Standard public schema';


