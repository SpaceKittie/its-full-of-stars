with apod as (
    select * from {{ ref('air_apod') }}
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
from apod
where APOD_DATE = (select max(APOD_DATE) from apod) 


