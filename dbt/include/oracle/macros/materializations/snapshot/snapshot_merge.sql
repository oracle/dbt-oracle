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
{% macro oracle__snapshot_merge_sql(target, source, insert_cols) -%}
    {%- set insert_cols_csv = [] -%}

    {% for column in insert_cols %}
      {% do insert_cols_csv.append("DBT_INTERNAL_SOURCE." + column) %}
    {% endfor %}

    {%- set dest_cols_csv = [] -%}

    {% for column in insert_cols %}
      {% do dest_cols_csv.append("DBT_INTERNAL_DEST." + column) %}
    {% endfor %}

    {%- set columns = config.get("snapshot_table_column_names") or get_snapshot_table_column_names() -%}

    merge into {{ target }} DBT_INTERNAL_DEST
    using {{ source }} DBT_INTERNAL_SOURCE
    on (DBT_INTERNAL_SOURCE.{{ columns.dbt_scd_id }} = DBT_INTERNAL_DEST.{{ columns.dbt_scd_id }})

    when matched
        then update
        set {{ columns.dbt_valid_to }} = DBT_INTERNAL_SOURCE.{{ columns.dbt_valid_to }}
        where
          {% if config.get("dbt_valid_to_current") %}
            (DBT_INTERNAL_DEST.{{ columns.dbt_valid_to }} = {{ config.get('dbt_valid_to_current') }} or
            DBT_INTERNAL_DEST.{{ columns.dbt_valid_to }} is null)
          {% else %}
            DBT_INTERNAL_DEST.{{ columns.dbt_valid_to }} is null
          {% endif %}
          and DBT_INTERNAL_SOURCE.dbt_change_type in ('update', 'delete')
    when not matched
        then insert ({{ dest_cols_csv | join(', ') }})
        values ({{ insert_cols_csv | join(', ') }})
        where DBT_INTERNAL_SOURCE.dbt_change_type = 'insert'
{% endmacro %}
