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
    {%- set dest_columns = adapter.get_columns_in_relation(target_relation) -%}
    {%- set dest_cols_csv = dest_columns | map(attribute='name') | join(', ') -%}

    {%- if unique_key is not none -%}
    delete
    from {{ target_relation }}
    where ({{ unique_key }}) in (
        select ({{ unique_key }})
        from {{ tmp_relation }}
    );
    {%- endif %}

    insert into {{ target_relation }} ({{ dest_cols_csv }})
    (
       select {{ dest_cols_csv }}
       from {{ tmp_relation }}
    )
{%- endmacro %}

{% macro oracle_incremental_upsert(tmp_relation, target_relation, dest_columns, unique_key=none, statement_name="main") %}
    {%- set on_predicates = [] -%}
    {%- set unique_key_list = [] -%}
    {%- set dest_cols_csv = dest_columns | map(attribute='name') | join(', ') -%}

    {%- if unique_key -%}
        {% if unique_key is sequence and unique_key is not mapping and unique_key is not string %}
          {% for key in unique_key | unique %}
                {% do unique_key_list.append(key.upper()) %}
            {% endfor %}
        {% else %}
            {% do unique_key_list.append(unique_key.upper()) %}
        {% endif %}
        {% for key in unique_key_list %}
            {% set this_key_match %}
                    temp.{{ key }} = target.{{ key }}
            {% endset %}
            {% do on_predicates.append(this_key_match) %}
        {% endfor %}
        merge into {{ target_relation }} target
          using {{ tmp_relation }} temp
          on ({{ on_predicates | join(' AND ') }})
        when matched then
          update set
          {% for col in dest_columns if col.name.upper() not in unique_key_list -%}
            target.{{ col.name }} = temp.{{ col.name }}{% if not loop.last %}, {% endif %}
          {% endfor -%}
        when not matched then
          insert({{ dest_cols_csv }})
          values(
            {% for col in dest_columns -%}
              temp.{{ col.name }}{% if not loop.last %}, {% endif %}
            {% endfor -%}
          )
    {%- else -%}
    insert into {{ target_relation }} ({{ dest_cols_csv }})
    (
       select {{ dest_cols_csv }}
       from {{ tmp_relation }}
    )
    {%- endif -%}
{%- endmacro %}
