-- air_traffic --
INSERT INTO osmaxx.transport_l
  SELECT
    osm_id             AS osm_id,
    osm_timestamp      AS lastchange,
    CASE
      WHEN osm_id < 0 THEN 'R' -- R=Relation
      ELSE 'W'                 -- W=Way
    END                AS geomtype,
    ST_Multi(way)      AS geom,
    'air_traffic'      AS aggtype,
    aeroway            AS type,
    name               AS name,
    "name:en"          AS name_en,
    "name:fr"          AS name_fr,
    "name:es"          AS name_es,
    "name:de"          AS name_de,
    int_name           AS name_int,
    CASE
      WHEN name IS NOT NULL AND name = osml10n_translit(name) THEN name
      WHEN "name:en" IS NOT NULL THEN "name:en"
      WHEN "name:fr" IS NOT NULL THEN "name:fr"
      WHEN "name:es" IS NOT NULL THEN "name:es"
      WHEN "name:de" IS NOT NULL THEN "name:de"
      WHEN int_name IS NOT NULL THEN osml10n_translit(int_name)
      WHEN name IS NOT NULL THEN osml10n_translit(name)
      ELSE NULL
    END                AS label,
    cast(tags AS TEXT) AS tags
  FROM osm_line
  WHERE aeroway IN ('runway', 'taxiway', 'apron')
UNION
  (
    WITH osm_single_polygon AS (
        SELECT
          osm_id,
          osm_timestamp,
          aeroway,
          name,
          "name:en",
          "name:fr",
          "name:es",
          "name:de",
          int_name,
          tags,

          CASE WHEN ST_GeometryType(way) = ANY (ARRAY ['ST_MultiPolygon', 'ST_Polygon'])
            THEN ST_Boundary(way)
          ELSE way
          END AS way
        FROM osm_polygon
    )
    SELECT
      osm_id             AS osm_id,
      osm_timestamp      AS lastchange,
      CASE
      WHEN osm_id < 0
        THEN 'R' -- R=Relation
      ELSE 'W' -- W=Way
      END                AS geomtype,
      ST_Multi(way)      AS geom,
      'air_traffic'      AS aggtype,
      aeroway            AS type,
      name               AS name,
      "name:en"          AS name_en,
      "name:fr"          AS name_fr,
      "name:es"          AS name_es,
      "name:de"          AS name_de,
      int_name           AS name_int,
      CASE
        WHEN name IS NOT NULL AND name = osml10n_translit(name) THEN name
        WHEN "name:en" IS NOT NULL THEN "name:en"
        WHEN "name:fr" IS NOT NULL THEN "name:fr"
        WHEN "name:es" IS NOT NULL THEN "name:es"
        WHEN "name:de" IS NOT NULL THEN "name:de"
        WHEN int_name IS NOT NULL THEN osml10n_translit(int_name)
        WHEN name IS NOT NULL THEN osml10n_translit(name)
        ELSE NULL
      END                AS label,
      cast(tags AS TEXT) AS tags
    FROM osm_single_polygon
    WHERE aeroway IN ('runway', 'taxiway', 'apron')
  );
