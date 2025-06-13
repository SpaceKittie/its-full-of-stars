with iss_stg as (
    select 
        LATITUDE,
        LONGITUDE,
        RETRIEVED_AT
    from {{ ref('air_iss_location') }}
),

iss_with_lag as (
    select
        LATITUDE,
        LONGITUDE,
        RETRIEVED_AT,
        lag(LATITUDE) over (order by RETRIEVED_AT) as PREV_LATITUDE,
        lag(LONGITUDE) over (order by RETRIEVED_AT) as PREV_LONGITUDE,
        lag(RETRIEVED_AT) over (order by RETRIEVED_AT) as PREV_RETRIEVED_AT
    from iss_stg
),

iss_enriched as (
    select
        LATITUDE,
        LONGITUDE,
        RETRIEVED_AT,
        st_distance(
            st_makepoint(LONGITUDE, LATITUDE), 
            st_makepoint(PREV_LONGITUDE, PREV_LATITUDE)
        ) / 1000 as DISTANCE_TRAVELED_KM,
        timediff(second, PREV_RETRIEVED_AT, RETRIEVED_AT) / 3600.0 as TIME_DIFF_HOURS
    from iss_with_lag
    where PREV_LATITUDE is not null and PREV_LONGITUDE is not null
)

select
    LATITUDE,
    LONGITUDE,
    RETRIEVED_AT,
    DISTANCE_TRAVELED_KM,
    case
        when TIME_DIFF_HOURS > 0 and DISTANCE_TRAVELED_KM / TIME_DIFF_HOURS > 0 
            then DISTANCE_TRAVELED_KM / TIME_DIFF_HOURS
        else 27600
    end as SPEED_KPH
from iss_enriched
order by RETRIEVED_AT desc 