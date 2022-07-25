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
      {% do insert_cols_csv.append("s." + column) %}
    {% endfor %}

    {%- set dest_cols_csv = [] -%}

    {% for column in insert_cols %}
      {% do dest_cols_csv.append("d." + column) %}
    {% endfor %}

    merge into {{ target }} d
    using {{ source }} s
    on (s.dbt_scd_id = d.dbt_scd_id)

    when matched
        then update
        set dbt_valid_to = s.dbt_valid_to
        where d.dbt_valid_to is null
          and s.dbt_change_type in ('update', 'delete')
    when not matched
        then insert ({{ dest_cols_csv | join(', ') }})
        values ({{ insert_cols_csv | join(', ') }})
        where s.dbt_change_type = 'insert'
{% endmacro %}
