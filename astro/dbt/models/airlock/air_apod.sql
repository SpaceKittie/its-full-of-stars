with apod_source as (
    select
        COPYRIGHT,
        APOD_DATE,
        EXPLANATION,
        HD_URL,
        MEDIA_TYPE,
        TITLE,
        URL,
        URL as IMAGE_URL,
        LOAD_TS
    from {{ source('cargo_bay', 'apod') }}
)

select
    COPYRIGHT,
    APOD_DATE,
    EXPLANATION,
    HD_URL,
    MEDIA_TYPE,
    TITLE,
    URL,
    IMAGE_URL,
    LOAD_TS
from apod_source 