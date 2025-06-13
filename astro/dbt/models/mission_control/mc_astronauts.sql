with staged_astronauts as (

    select * from {{ ref('air_astronauts') }}

),

mission_control_astronauts as (

    select
        ID as ASTRONAUT_ID,
        NAME,
        STATUS,
        AGENCY,
        NATIONALITY,
        IS_IN_SPACE,
        CURRENT_CRAFT,
        AGE,
        BIO,
        PROFILE_IMAGE,
        WIKI as WIKIPEDIA_URL,
        LOAD_TS
        
    from staged_astronauts
    where AGENCY is not null and NAME is not null

)

select * from mission_control_astronauts