{{config(materialized='incremental', unique_key='group_id')}}
WITH direct_sales_promo_cost AS (
    SELECT s.prod_id,
           s.quantity_sold,
           s.amount_sold,
           s.time_id,
           c.channel_desc,
           p.promo_name,
           p.promo_cost,
           {{ hash_arguments(['s.prod_id', 's.quantity_sold', 's.time_id', 'p.promo_name']) }} AS group_id
    FROM {{ source('sh_database', 'sales') }} s,
         {{ source('sh_database', 'promotions') }} p,
         {{ source('sh_database', 'channels') }} c
    WHERE s.channel_id = 3
    AND s.promo_id = p.promo_id
    AND s.channel_id = c.channel_id
    {% if is_incremental() %}
        AND s.time_id > (SELECT MAX(time_id) FROM {{ this }})
    {% endif %}
)
SELECT * FROM direct_sales_promo_cost