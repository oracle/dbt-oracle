{{ config(materialized='table') }}

  SELECT 
    Cast (prop_data.property_id as int) property_id,
    mort_data.mortgage_id,
    prop_data.property_type,
    prop_data.living_area,
    --mort_data.create_date --zum zeigen von Enforce Model (contract sagt Date, aber ohne Spezification wird es Timestamp) (Null/Fehler bei Testdaten wird auch erkannt)
    Cast( mort_data.create_date as date) create_date
FROM 
    {{ ref('mortgage_application_seed') }}  mort_data
LEFT JOIN 
    {{ ref('property_data_seed') }}  prop_data
ON 
    prop_data.property_id = mort_data.mortgage_id
