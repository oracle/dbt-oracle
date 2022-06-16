{{config(materialized='table')}}
WITH direct_sales_promo_cost AS (
    SELECT s.prod_id,
           s.quantity_sold,
           s.amount_sold,
           s.time_id,
           c.channel_desc,
           p.promo_name,
           p.promo_cost
    FROM {{ source('sh_database', 'sales') }} s,
         {{ source('sh_database', 'promotions') }} p,
         {{ source('sh_database', 'channels') }} c
    WHERE s.channel_id = 3
    AND s.promo_id = p.promo_id
    AND s.channel_id = c.channel_id
)
SELECT * FROM direct_sales_promo_cost