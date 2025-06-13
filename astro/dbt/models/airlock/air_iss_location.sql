with iss_location_source as (
    select
        LOAD_TS as RETRIEVED_AT,
        LATITUDE::double as LATITUDE,
        LONGITUDE::double as LONGITUDE,
        API_TIMESTAMP::timestamp_ntz as API_TIMESTAMP
    from {{ source('cargo_bay', 'iss_location') }}
)

select
    RETRIEVED_AT,
    LATITUDE,
    LONGITUDE,
    API_TIMESTAMP
from iss_location_source 