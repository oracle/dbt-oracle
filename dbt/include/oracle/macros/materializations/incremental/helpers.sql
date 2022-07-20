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

{% macro oracle_conditional_quote_column_names_for_incremental_merge(dest_columns) %}
    {%- set quote = "\"" -%}
    {%- set final_update_columns = [] -%}
    {%- set user_defined_merge_update_columns = config.get("merge_update_columns") -%}
    {% if user_defined_merge_update_columns is none %}
        {%- set final_update_columns = dest_columns | map(attribute='name') -%}
    {% else %}
        {% for col in user_defined_merge_update_columns %}
            {% if adapter.should_identifier_be_quoted(col) == true %}
                {% do final_update_columns.append(quote ~ col ~ quote) %}
            {% else %}
                {% do final_update_columns.append(col) %}
            {% endif %}
        {% endfor %}
    {% endif %}
    {{ return(final_update_columns)}}
{% endmacro %}

{% macro oracle_conditional_quote_unique_key_for_incremental_merge(unique_key) %}
    {%- set quote = "\"" -%}
    {%- set unique_key_list = [] -%}
    {%- set unique_key_merge_predicates = [] -%}
    {% if unique_key is sequence and unique_key is not mapping and unique_key is not string %}
          {% for key in unique_key | unique %}
                {% if adapter.should_identifier_be_quoted(key) == true %}
                    {% do unique_key_list.append(quote ~ key ~ quote) %}
                {% else %}
                    {% do unique_key_list.append(key.upper()) %}
                {% endif %}
            {% endfor %}
        {% else %}
            {% if adapter.should_identifier_be_quoted(unique_key) == true %}
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
    {%- set dest_cols_csv = dest_columns | map(attribute='name') | join(', ') -%}
    {%- set update_columns = oracle_conditional_quote_column_names_for_incremental_merge(dest_columns) -%}
    {%- if unique_key -%}
        {%- set unique_key_result = oracle_conditional_quote_unique_key_for_incremental_merge(unique_key) -%}
        {%- set unique_key_list = unique_key_result['unique_key_list'] -%}
        {%- set unique_key_merge_predicates = unique_key_result['unique_key_merge_predicates'] -%}
        merge into {{ target_relation }} target
          using {{ tmp_relation }} temp
          on ({{ unique_key_merge_predicates | join(' AND ') }})
        when matched then
          update set
          {% for col in update_columns if col.upper() not in unique_key_list -%}
            target.{{ col }} = temp.{{ col }}{% if not loop.last %}, {% endif %}
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
