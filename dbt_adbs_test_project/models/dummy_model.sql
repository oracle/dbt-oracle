{{ config(materialized='table') }}

SELECT
    id,
    label,
    current_timestamp AS created_at
FROM {{ ref('dummy_table') }}

