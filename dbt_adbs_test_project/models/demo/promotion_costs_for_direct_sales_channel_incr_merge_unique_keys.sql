{{config(materialized='incremental',
         on_schema_change='append_new_columns',
         unique_key=['prod_id', 'quantity_sold', 'time_id', 'promo_name'])}}
WITH direct_sales_promo_cost AS (
    SELECT s.prod_id,
           s.quantity_sold,
           s.amount_sold,
           s.time_id,
           s.cust_id,
           c.channel_desc,
           p.promo_name,
           p.promo_cost
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
