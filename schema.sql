/*
 * deliveryHunt database schema (DDL dump) for PostreSQL.
 */
-- Replace tables: drop + create
DROP TABLE IF EXISTS public.order;

DROP TABLE IF EXISTS public.address;

DROP TABLE IF EXISTS public."comment";

DROP TABLE IF EXISTS public.client;

DROP TABLE IF EXISTS public.courier;

DROP TABLE IF EXISTS public."user";

DROP TABLE IF EXISTS public.electric_vehicle;

DROP TABLE IF EXISTS public.electric_vehicle_type;

DROP TABLE IF EXISTS public.manufacturer;

/*
 By default for all tables:
 TABLESPACE pg_default;
 ALTER TABLE IF EXISTS public.electric_vehicle_type OWNER to postgres;
 */
BEGIN;

CREATE TYPE public.vehicle_type AS ENUM ('scooter', 'bike', 'moped', 'car');

CREATE TABLE IF NOT EXISTS public.manufacturer (
    id integer NOT NULL GENERATED ALWAYS AS IDENTITY (
        INCREMENT 1 START 15 MINVALUE 1 MAXVALUE 2147483647 CACHE 1
    ),
    "name" character varying(100) COLLATE pg_catalog."default" NOT NULL,
    "location" character varying(200) COLLATE pg_catalog."default",
    tax_number character(15) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT manufacturer_pkey PRIMARY KEY (id),
    CONSTRAINT manufacturer_unique_name UNIQUE (name),
    CONSTRAINT manufacturer_unique_tax UNIQUE (tax_number)
);

CREATE TABLE IF NOT EXISTS public.electric_vehicle_type (
    id integer NOT NULL GENERATED ALWAYS AS IDENTITY (
        INCREMENT 1 START 15 MINVALUE 1 MAXVALUE 2147483647 CACHE 1
    ),
    "name" character varying(100) COLLATE pg_catalog."default" NOT NULL,
    manufacturer integer,
    price real,
    battery_lifetime INTERVAL,
    vehicle_type vehicle_type NOT NULL,
    CONSTRAINT electric_vehicle_type_pkey PRIMARY KEY (id),
    CONSTRAINT electric_vehicle_type_manufacturer FOREIGN KEY (manufacturer) REFERENCES public.manufacturer (id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE NOT VALID,
    CONSTRAINT price_positive CHECK (price > 0 :: double precision),
    CONSTRAINT baterry_lifetime_is_positive CHECK (battery_lifetime >= 0) NOT VALID
);

CREATE TABLE public.electric_vehicle (
    id integer generated always AS identity (
        INCREMENT 1 START 15 MINVALUE 1 MAXVALUE 2147483647 CACHE 1
    ),
    "type" integer,
    mileage double precision,
    production_time timestamp,
    CONSTRAINT electric_vehicle_pkey PRIMARY KEY (id),
    CONSTRAINT electric_vehicle_type_fkey FOREIGN KEY (TYPE) REFERENCES public.electric_vehicle_type (id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE NOT VALID,
    CONSTRAINT mileage_is_positive CHECK (mileage >= 0)
);

CREATE TABLE IF NOT EXISTS public."user" (
    id integer NOT NULL GENERATED ALWAYS AS IDENTITY (
        INCREMENT 1 START 15 MINVALUE 1 MAXVALUE 2147483647 CACHE 1
    ),
    first_name character varying(20) COLLATE pg_catalog."default" NOT NULL,
    last_name character varying(20) COLLATE pg_catalog."default" NOT NULL,
    phone character varying(15) COLLATE pg_catalog."default" NOT NULL,
    "password" character(77) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT pkey PRIMARY KEY (id),
    CONSTRAINT first_last_names_unique UNIQUE (first_name, last_name)
);

CREATE TABLE IF NOT EXISTS public.courier (
    id integer NOT NULL,
    "user" integer NOT NULL,
    vehicle integer NOT NULL,
    passport character varying(20) COLLATE pg_catalog."default" NOT NULL,
    emploment_record character varying(20) COLLATE pg_catalog."default" NOT NULL,
    resident_place character varying(150) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT courier_pkey PRIMARY KEY (id),
    CONSTRAINT user_account_unique UNIQUE ("user"),
    CONSTRAINT courier_user_fk FOREIGN KEY ("user") REFERENCES public."user" (id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT courier_vehicle_fkey FOREIGN KEY (vehicle) REFERENCES public.electric_vehicle (id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE NOT VALID
);

CREATE INDEX IF NOT EXISTS fki_courier_vehicle_fkey ON public.courier USING btree (vehicle ASC NULLS LAST);

CREATE TABLE IF NOT EXISTS public.client (
    id integer NOT NULL GENERATED ALWAYS AS IDENTITY (
        INCREMENT 1 START 15 MINVALUE 1 MAXVALUE 2147483647 CACHE 1
    ),
    "user" integer NOT NULL,
    individual boolean NOT NULL DEFAULT TRUE,
    CONSTRAINT client_pkey PRIMARY KEY (id),
    CONSTRAINT client_user_unique UNIQUE ("user"),
    CONSTRAINT client_user_fk FOREIGN KEY ("user") REFERENCES public."user" (id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE public.address (
    id integer generated always AS identity (
        increment 1 START 15 minvalue 1 maxvalue 2147483647 cache 1
    ),
    street character varying (255) COLLATE pg_catalog."default" NOT NULL,
    building character varying (255) COLLATE pg_catalog."default" NOT NULL,
    entrance character varying (255) COLLATE pg_catalog."default" NOT NULL,
    intercom character varying (255) COLLATE pg_catalog."default" NOT NULL,
    "floor" character varying (255) COLLATE pg_catalog."default" NOT NULL,
    apartment character varying (255) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT address_pkey PRIMARY KEY (id)
);

CREATE TABLE public.comment (
    id integer generated always AS identity (
        increment 1 START 15 minvalue 1 maxvalue 2147483647
    ),
    "text" text,
    CONSTRAINT comment_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public."order" (
    id uuid NOT NULL,
    client integer NOT NULL,
    courier integer,
    create_time timestamp without time zone NOT NULL DEFAULT NOW(),
    address_from integer NOT NULL,
    address_to integer NOT NULL,
    "weight" real,
    COMMENT integer,
    max_delivery_time INTERVAL NOT NULL,
    take_time timestamp without time zone,
    deliver_time timestamp without time zone,
    delivered boolean,
    rate integer,
    CONSTRAINT order_pkey PRIMARY KEY (id),
    CONSTRAINT order_client_fk FOREIGN KEY (client) REFERENCES public.client (id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT order_comment_fk FOREIGN KEY (COMMENT) REFERENCES public.comment (id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT order_courier_fk FOREIGN KEY (courier) REFERENCES public.courier (id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT order_from_address_fk FOREIGN KEY (address_from) REFERENCES public.address (id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT order_to_address_fk FOREIGN KEY (address_to) REFERENCES public.address (id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT order_rate_between_1_and_5 CHECK (
        rate >= 1
        AND rate <= 5
    )
);

COMMIT;