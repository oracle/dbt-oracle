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

{% macro oracle_check_and_quote_column_names_for_incremental_merge(dest_column_names) %}
    {%- set quoted_update_columns = [] -%}
    {%- set update_columns = config.get("merge_update_columns", default=dest_column_names) -%}
    {% for col in update_columns %}
        {% do quoted_update_columns.append(adapter.check_and_quote_identifier(col, model.columns)) %}
    {% endfor %}
    {{ return(quoted_update_columns)}}
{% endmacro %}

{% macro oracle_check_and_quote_unique_key_for_incremental_merge(unique_key) %}
    {%- set quote = "\"" -%}
    {%- set unique_key_list = [] -%}
    {%- set unique_key_merge_predicates = [] -%}
    {% if unique_key is sequence and unique_key is not mapping and unique_key is not string %}
          {% for key in unique_key | unique %}
                {% if adapter.should_identifier_be_quoted(key, model.columns) == true %}
                    {% do unique_key_list.append(quote ~ key ~ quote) %}
                {% else %}
                    {% do unique_key_list.append(key.upper()) %}
                {% endif %}
            {% endfor %}
        {% else %}
            {% if adapter.should_identifier_be_quoted(unique_key, model.columns) == true %}
                {% do unique_key_list.append(quote ~ unique_key ~ quote) %}
            {% else %}
                {% do unique_key_list.append(unique_key.upper()) %}
            {% endif %}
        {% endif %}
        {% for key in unique_key_list %}
            {% set this_key_match %}
                    temp.{{ key }} = target.{{ key }}
            {% endset %}
            {% do unique_key_merge_predicates.append(this_key_match) %}
        {% endfor %}
    {%- set unique_key_result = {'unique_key_list': unique_key_list, 'unique_key_merge_predicates': unique_key_merge_predicates} -%}
    {{ return(unique_key_result)}}
{% endmacro %}


{% macro oracle_incremental_upsert(tmp_relation, target_relation, dest_columns, unique_key=none, statement_name="main") %}
    {%- set dest_column_names = dest_columns | map(attribute='name') | list -%}
    {%- set dest_cols_csv = get_quoted_column_csv(model, dest_column_names)  -%}
    {%- set update_columns = oracle_check_and_quote_column_names_for_incremental_merge(dest_column_names) -%}
    {%- if unique_key -%}
        {%- set unique_key_result = oracle_check_and_quote_unique_key_for_incremental_merge(unique_key) -%}
        {%- set unique_key_list = unique_key_result['unique_key_list'] -%}
        {%- set unique_key_merge_predicates = unique_key_result['unique_key_merge_predicates'] -%}
        merge into {{ target_relation }} target
          using {{ tmp_relation }} temp
          on ({{ unique_key_merge_predicates | join(' AND ') }})
        when matched then
          update set
          {% for col in update_columns if (col.upper() not in unique_key_list and col not in unique_key_list) -%}
            target.{{ col }} = temp.{{ col }}{% if not loop.last %}, {% endif %}
          {% endfor -%}
        when not matched then
          insert({{ dest_cols_csv }})
          values(
            {% for col in dest_columns -%}
              temp.{{ adapter.check_and_quote_identifier(col.name, model.columns) }}{% if not loop.last %}, {% endif %}
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
