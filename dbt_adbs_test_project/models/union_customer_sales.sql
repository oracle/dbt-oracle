{{ config(materialized='table')}}
{{
    dbt_utils.union_relations(
        relations=[source('sh_database', 'sales'),
                   source('sh_database', 'customers')],
        source_column_name='dbt_source_relation')
}}
