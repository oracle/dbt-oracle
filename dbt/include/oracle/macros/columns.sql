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
{% macro oracle__alter_relation_add_remove_columns(relation, add_columns, remove_columns) %}

  {% if add_columns is none %}
    {% set add_columns = [] %}
  {% endif %}
  {% if remove_columns is none %}
    {% set remove_columns = [] %}
  {% endif %}
{# To avoid ORA-12987: cannot combine drop column with other operations, we execute 2 different SQL for add and drop respectively #}

{% if add_columns|length > 0 %}
  {% set add_sql %}
          ALTER {{ relation.type }} {{ relation }}
              ADD (
              {% for column in add_columns %}
                {{ adapter.check_and_quote_identifier(column.name, model.columns) }} {{ column.data_type }}{{ ',' if not loop.last }}
              {% endfor %}
              )
  {% endset %}
  {% do run_query(add_sql)%}
{% endif %}

{% if remove_columns|length > 0 %}
    {% set remove_sql %}
          ALTER {{ relation.type }} {{ relation }}
              DROP (
                {% for column in remove_columns %}
                  {{ adapter.check_and_quote_identifier(column.name, model.columns) }}{{ ',' if not loop.last }}
                {% endfor %}
                ) CASCADE CONSTRAINTS
   {% endset %}
   {% do run_query(remove_sql)%}
{% endif %}
{% endmacro %}

{% macro get_quoted_column_csv(model, column_names) %}
    {%- set quoted = [] -%}
    {% for col in column_names %}
        {%- do quoted.append(adapter.check_and_quote_identifier(col, model.columns)) -%}
     {% endfor %}
    {%- set cols_csv = quoted | join(', ') -%}
    {{ return(cols_csv) }}
{% endmacro %}