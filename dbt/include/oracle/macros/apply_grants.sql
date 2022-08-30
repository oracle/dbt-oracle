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

{% macro oracle__get_show_grant_sql(relation) %}
    {# SQL that returns the current grants (grantee-privilege pairs) #}
    SELECT grantee as "grantee", privilege as "privilege_type"
    FROM SYS.ALL_TAB_PRIVS
    WHERE UPPER(table_name) = UPPER('{{ relation.identifier }}')
    {% if relation.schema %}
        AND UPPER(table_schema) = UPPER('{{ relation.schema }}')
    {% endif %}
{% endmacro %}

{% macro oracle__call_dcl_statements(dcl_statement_list) %}
     {# Run each grant/revoke statement against the database. This is the culmination of apply_grants() #}
     {% for dcl_statement in dcl_statement_list %}
        {% do run_query(dcl_statement) %}
     {% endfor %}
{% endmacro %}
