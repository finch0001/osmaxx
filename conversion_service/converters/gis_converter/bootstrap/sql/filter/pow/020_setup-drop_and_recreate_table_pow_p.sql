-----------------
----  pow_p ----
-----------------
DROP TABLE if exists osmaxx.pow_p;
CREATE TABLE osmaxx.pow_p (
	osm_id bigint,
	lastchange timestamp without time zone,
	geomtype text,
	geom geometry(POINT,900913),
	aggtype text,
	type text,
	name text,
	name_en text,
	name_fr text,
	name_es text,
	name_de text,
	int_name text,
	label text,
	tags text,
	website text,
	wikipedia text,
	phone text,
	contact_phone text,
	opening_hours text,
	"access" text
);
