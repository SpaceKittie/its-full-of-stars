with spacedevs_astronauts as (

    select * from {{ source('cargo_bay', 'astronauts') }}

),

in_space_now as (

    select
        *,
        row_number() over (partition by lower(trim(NAME)) order by LOAD_TS desc) as rn
    from {{ source('cargo_bay', 'in_space') }}

),

astronauts_enriched as (

    select
        s.ID,
        s.URL,
        s.NAME,
        s.STATUS:name::string as STATUS,
        s.TYPE:name::string as TYPE,
        i.NAME is not null as IS_IN_SPACE,
        s.TIME_IN_SPACE,
        s.EVA_TIME,
        s.AGE,
        s.DATE_OF_BIRTH,
        s.DATE_OF_DEATH,
        s.NATIONALITY,
        s.BIO,
        s.TWITTER,
        s.INSTAGRAM,
        s.WIKI,
        s.AGENCY:name::string as AGENCY,
        s.PROFILE_IMAGE,
        s.PROFILE_IMAGE_THUMBNAIL,
        s.FLIGHTS_COUNT,
        s.LANDINGS_COUNT,
        s.SPACEWALKS_COUNT,
        s.LAST_FLIGHT,
        s.FIRST_FLIGHT,
        i.CRAFT as CURRENT_CRAFT,
        s.LOAD_TS

    from spacedevs_astronauts s
    left join in_space_now i
        on lower(trim(s.NAME)) = lower(trim(i.NAME))
        and i.rn = 1

)

select * from astronauts_enriched