{#
 Copyright (c) 2022, Oracle and/or its affiliates.
 Copyright (c) 2020, Vitor Avancini

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

     https://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
#}

{% macro oracle__current_timestamp() -%}
  SYS_EXTRACT_UTC(current_timestamp)
{%- endmacro %}

{% macro oracle__snapshot_string_as_time(timestamp) -%}
    {%- set result = "TO_TIMESTAMP('"~ timestamp ~ "','yyyy/mm/dd hh24:mi:ss.FF')" -%}
    {{ return(result) }}
{%- endmacro %}

{% macro get_snapshot_get_time_data_type() %}
    {% set snapshot_time = adapter.dispatch('snapshot_get_time', 'dbt')() %}
    {% set time_data_type_sql = 'select ' ~ snapshot_time ~ ' as dbt_snapshot_time from dual' %}
    {% set snapshot_time_column_schema = get_column_schema_from_query(time_data_type_sql) %}
    {% set time_data_type = snapshot_time_column_schema[0].dtype %}
    {{ return(time_data_type or none) }}
{% endmacro %}