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
{# Returns difference (in integer) between 2 dates #}
{% macro oracle__datediff(first_date, second_date, datepart) %}
    {%- set single_quote = "\'" -%}
    {%- set D2S_INTERVAL_UNITS = ['DAY', 'HOUR', 'MINUTE', 'SECOND'] -%}
    {% if datepart.upper() in D2S_INTERVAL_UNITS %}
        ROUND((CAST({{ second_date }} AS DATE) - CAST({{ first_date }} AS DATE)) *
               decode(upper({{single_quote ~ datepart ~ single_quote}}),
                      'HOUR', 24,
                      'MINUTE', 24*60,
                      'SECOND', 24*60*60,
                      1))
    {% elif datepart.upper() == 'WEEK' %}
        ROUND((CAST({{ second_date }} AS DATE) - CAST({{ first_date }} AS DATE))/7)
    {% elif datepart.upper() == 'MONTH' %}
        ROUND((MONTHS_BETWEEN(CAST({{second_date}} AS DATE), CAST({{first_date}} AS DATE))))
    {% elif datepart.upper() == 'QUARTER' %}
        ROUND((MONTHS_BETWEEN(CAST({{second_date}} AS DATE), CAST({{first_date}} AS DATE))/3))
    {% elif datepart.upper() == 'YEAR' %}
        ROUND((MONTHS_BETWEEN(CAST({{second_date}} AS DATE), CAST({{first_date}} AS DATE))/12))
    {% endif %}
{% endmacro %}
