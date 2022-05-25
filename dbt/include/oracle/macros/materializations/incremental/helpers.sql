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
{% macro oracle_incremental_upsert_backup(tmp_relation, target_relation, unique_key=none, statement_name="main") %}
    {%- set temp_columns = adapter.get_columns_in_relation(target_relation) | map(attribute='name') -%}
    {%- set dest_columns = [] -%}
    {%- for col in temp_columns -%}
      {%- do dest_columns.append('"{}"'.format(col) | upper) -%}
    {%- endfor -%}
    {%- set dest_cols_csv = dest_columns | join(', ') -%}

    {%- if unique_key is not none -%}
    delete
    from {{ '"{}"'.format(target_relation).replace('.', '"."') | upper }}
    where ({{ '"{}"'.format(unique_key) }}) in (
      select ({{ '"{}"'.format(unique_key) }})
      from {{ '"{}"'.format(tmp_relation).replace('.', '"."') | upper }}
    );
    {%- endif %}

    insert into {{ '"{}"'.format(target_relation).replace('.', '"."') | upper }} ({{ dest_cols_csv }})
    (
      select {{ dest_cols_csv }}
      from {{ '"{}"'.format(tmp_relation).replace('.', '"."') | upper }}
    )
{%- endmacro %}

{% macro oracle_incremental_upsert(tmp_relation, target_relation, unique_key=none, statement_name="main") %}
    {%- set temp_columns = adapter.get_columns_in_relation(target_relation) | map(attribute='name') -%}
    {%- set dest_columns = [] -%}
    {%- for col in temp_columns -%}
      {%- do dest_columns.append('"{}"'.format(col) | upper) -%}
    {%- endfor -%}
    {%- set dest_cols_csv = dest_columns | join(', ') -%}

    {%- if unique_key is not none -%}
    merge into {{ '"{}"'.format(target_relation).replace('.', '"."') | upper }} target
      using {{ '"{}"'.format(tmp_relation).replace('.', '"."') | upper }} temp
      on (temp.{{ unique_key }} = target.{{ unique_key }})
    when matched then
      update set
      {% for col in dest_columns if col != unique_key -%}
        target.{{ col }} = temp.{{ col }}{% if not loop.last %}, {% endif %}
      {% endfor -%}
    when not matched then
      insert({{ dest_cols_csv }})
      values(
        {% for col in dest_columns -%}
          temp.{{ col }}{% if not loop.last %}, {% endif %}
        {% endfor -%}
      )
    {%- else -%}
    insert into {{ '"{}"'.format(target_relation).replace('.', '"."') | upper }} ({{ dest_cols_csv }})
    (
       select {{ dest_cols_csv }}
       from {{ '"{}"'.format(tmp_relation).replace('.', '"."') | upper }}
    )
    {%- endif -%}
{%- endmacro %}
