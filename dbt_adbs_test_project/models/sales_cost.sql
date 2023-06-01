{{ config(materialized='table')}}
with sales_cost_cte as(
    select prod_id,
           cast(time_id as TIMESTAMP) as cost_timestamp,
           promo_id,
           channel_id,
           unit_cost,
           unit_price
    from {{ source('sh_database', 'costs') }}
)
select * from sales_cost_cte