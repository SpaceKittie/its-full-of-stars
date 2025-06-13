{% macro create_raw_tables() %}
    {% do run_query("CREATE TABLE IF NOT EXISTS CB_ISS_LOCATION (LATITUDE FLOAT, LONGITUDE FLOAT, API_TIMESTAMP TIMESTAMP_LTZ, LOAD_TS TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP())") %}
    {% do run_query("CREATE TABLE IF NOT EXISTS CB_NASA_APOD (COPYRIGHT VARCHAR, APOD_DATE TIMESTAMP_LTZ, EXPLANATION VARCHAR, HD_URL VARCHAR, MEDIA_TYPE VARCHAR, SERVICE_VERSION VARCHAR, TITLE VARCHAR, URL VARCHAR, LOAD_TS TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP())") %}
    {% do run_query("""
        CREATE TABLE IF NOT EXISTS CB_ASTRONAUTS (
            ID                          INTEGER PRIMARY KEY,
            URL                         VARCHAR,
            NAME                        VARCHAR,
            STATUS                      VARIANT,
            TYPE                        VARIANT,
            IN_SPACE                    BOOLEAN,
            TIME_IN_SPACE               VARCHAR,
            EVA_TIME                    VARCHAR,
            AGE                         INTEGER,
            DATE_OF_BIRTH               DATE,
            DATE_OF_DEATH               DATE,
            NATIONALITY                 VARCHAR,
            BIO                         VARCHAR,
            TWITTER                     VARCHAR,
            INSTAGRAM                   VARCHAR,
            WIKI                        VARCHAR,
            AGENCY                      VARIANT,
            PROFILE_IMAGE               VARCHAR,
            PROFILE_IMAGE_THUMBNAIL     VARCHAR,
            FLIGHTS_COUNT               INTEGER,
            LANDINGS_COUNT              INTEGER,
            SPACEWALKS_COUNT            INTEGER,
            LAST_FLIGHT                 TIMESTAMP_LTZ,
            FIRST_FLIGHT                TIMESTAMP_LTZ,
            LOAD_TS                     TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
        )
    """) %}
    {% do run_query("""
        CREATE TABLE IF NOT EXISTS CB_IN_SPACE (
            NAME                        VARCHAR,
            CRAFT                       VARCHAR,
            LOAD_TS                     TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
        )
    """) %}
    {% do log('create_raw_tables macro executed', info=True) %}
{% endmacro %}