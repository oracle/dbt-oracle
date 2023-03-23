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

{% macro oracle_check_and_quote_unique_key_for_incremental_merge(unique_key, incremental_predicates=none) %}
    {%- set quote = "\"" -%}
    {%- set unique_key_list = [] -%}
    {%- set unique_key_merge_predicates = [] if incremental_predicates is none else [] + incremental_predicates -%}
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
            DBT_INTERNAL_SOURCE.{{ key }} = DBT_INTERNAL_DEST.{{ key }}
        {% endset %}
        {% do unique_key_merge_predicates.append(this_key_match) %}
    {% endfor %}
    {%- set unique_key_result = {'unique_key_list': unique_key_list, 'unique_key_merge_predicates': unique_key_merge_predicates} -%}
    {{ return(unique_key_result)}}
{% endmacro %}


{% macro oracle__get_merge_update_columns(merge_update_columns, merge_exclude_columns, dest_columns) %}
  {%- set default_cols = dest_columns | map(attribute='name') | list -%}

  {%- if merge_update_columns and merge_exclude_columns -%}
    {{ exceptions.raise_compiler_error(
        'Model cannot specify merge_update_columns and merge_exclude_columns. Please update model to use only one config'
    )}}
  {%- elif merge_update_columns -%}
    {%- set update_columns = merge_update_columns -%}
  {%- elif merge_exclude_columns -%}
    {%- set update_columns = [] -%}
    {%- for column in dest_columns -%}
      {% if column.column | lower not in merge_exclude_columns | map("lower") | list %}
        {%- do update_columns.append(column.name) -%}
      {% endif %}
    {%- endfor -%}
  {%- else -%}
    {%- set update_columns = default_cols -%}
  {%- endif -%}

   {%- set quoted_update_columns = [] -%}
   {% for col in update_columns %}
        {% do quoted_update_columns.append(adapter.check_and_quote_identifier(col, model.columns)) %}
   {% endfor %}
   {{ return(quoted_update_columns)}}
{% endmacro %}


{% macro oracle__get_incremental_append_sql(args_dict) %}
    {%- set parallel = config.get('parallel', none) -%}
    {%- set dest_columns = args_dict["dest_columns"] -%}
    {%- set temp_relation = args_dict["temp_relation"] -%}
    {%- set target_relation = args_dict["target_relation"] -%}
    {%- set dest_column_names = dest_columns | map(attribute='name') | list -%}
    {%- set dest_cols_csv = get_quoted_column_csv(model, dest_column_names)  -%}
    INSERT {% if parallel %} /*+PARALLEL({{ parallel }})*/ {% endif %} INTO {{ target_relation }} ({{ dest_cols_csv }})
    (
       SELECT {{ dest_cols_csv }}
       FROM {{ temp_relation }}
    )
{% endmacro %}

{% macro oracle__get_incremental_merge_sql(args_dict) %}
    {%- set parallel = config.get('parallel', none) -%}
    {%- set dest_columns = args_dict["dest_columns"] -%}
    {%- set temp_relation = args_dict["temp_relation"] -%}
    {%- set target_relation = args_dict["target_relation"] -%}
    {%- set unique_key = args_dict["unique_key"] -%}
    {%- set dest_column_names = dest_columns | map(attribute='name') | list -%}
    {%- set dest_cols_csv = get_quoted_column_csv(model, dest_column_names)  -%}
    {%- set merge_update_columns = config.get('merge_update_columns') -%}
    {%- set merge_exclude_columns = config.get('merge_exclude_columns') -%}
    {%- set incremental_predicates = args_dict["incremental_predicates"] -%}
    {%- set update_columns = get_merge_update_columns(merge_update_columns, merge_exclude_columns, dest_columns) -%}
    {%- if unique_key -%}
        {%- set unique_key_result = oracle_check_and_quote_unique_key_for_incremental_merge(unique_key, incremental_predicates) -%}
        {%- set unique_key_list = unique_key_result['unique_key_list'] -%}
        {%- set unique_key_merge_predicates = unique_key_result['unique_key_merge_predicates'] -%}
        merge {% if parallel %} /*+parallel({{ parallel }})*/ {% endif %} into {{ target_relation }} DBT_INTERNAL_DEST
          using {{ temp_relation }} DBT_INTERNAL_SOURCE
          on ({{ unique_key_merge_predicates | join(' AND ') }})
        when matched then
          update set
          {% for col in update_columns if (col.upper() not in unique_key_list and col not in unique_key_list) -%}
            DBT_INTERNAL_DEST.{{ col }} = DBT_INTERNAL_SOURCE.{{ col }}{% if not loop.last %}, {% endif %}
          {% endfor -%}
        when not matched then
          insert({{ dest_cols_csv }})
          values(
            {% for col in dest_columns -%}
              DBT_INTERNAL_SOURCE.{{ adapter.check_and_quote_identifier(col.name, model.columns) }}{% if not loop.last %}, {% endif %}
            {% endfor -%}
          )
    {%- else -%}
    insert {% if parallel %} /*+parallel({{ parallel }})*/ {% endif %} into  {{ target_relation }} ({{ dest_cols_csv }})
    (
       select {{ dest_cols_csv }}
       from {{ temp_relation }}
    )
    {%- endif -%}
{% endmacro %}

{% macro oracle__get_incremental_default_sql(arg_dict) %}
  {% do return(get_incremental_merge_sql(arg_dict)) %}
{% endmacro %}
