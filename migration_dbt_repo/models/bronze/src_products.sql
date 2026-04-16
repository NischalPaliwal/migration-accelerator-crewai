{{
    config(
        materialized = 'table',
        tags         = ['bronze', 'raw']
    )
}}

select
    prod_id,
    prod_name,
    cat_id,
    base_price,
    status,
    updated_at
from
    {{ source('nischal', 'src_products') }}