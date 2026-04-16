{{
    config(
        materialized = 'table',
        tags         = ['bronze', 'raw']
    )
}}

select
    cat_id,
    cat_name,
    dept_code,
    extract_ts
from
    {{ source('nischal', 'src_categories') }}