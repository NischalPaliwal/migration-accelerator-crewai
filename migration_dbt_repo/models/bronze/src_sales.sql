{{
    config(
        materialized = 'table',
        tags         = ['bronze', 'raw']
    )
}}

select
    txn_id,
    prod_id,
    qty,
    price_paid,
    txn_date,
    store_id
from
    {{ source('nischal', 'src_sales') }}