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
{# Returns date with the 'datepart' portion truncated #}
{% macro oracle__date_trunc(datepart, date) %}
    {% if datepart.upper() == 'QUARTER' %}
        {% set datepart = 'Q' %}
    {% endif %}
    {% if datepart.upper() == 'WEEK' %}
        {% set datepart = 'WW' %}
    {% endif %}
    {%- set single_quote = "\'" -%}
    TRUNC({{date}}, {{single_quote ~ datepart ~ single_quote}})
{% endmacro %}
