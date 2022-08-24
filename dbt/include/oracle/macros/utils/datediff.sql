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
{# Returns difference (as an integer) in between 2 dates #}
{% macro oracle__datediff(first_date, second_date, datepart) %}
    {% if datepart.upper() == 'YEAR' %}
        ROUND(MONTHS_BETWEEN(TRUNC(CAST({{second_date}} AS DATE), 'YEAR'), TRUNC(CAST({{first_date}} AS DATE), 'YEAR'))/12)
    {% elif datepart.upper() == 'QUARTER' %}
        ROUND(MONTHS_BETWEEN(TRUNC(CAST({{second_date}} AS DATE), 'Q'), TRUNC(CAST({{first_date}} AS DATE), 'Q'))/3)
    {% elif datepart.upper() == 'MONTH'%}
        ROUND(MONTHS_BETWEEN(TRUNC(CAST({{second_date}} AS DATE), 'MONTH'), TRUNC(CAST({{first_date}} AS DATE), 'MONTH')))
    {% elif datepart.upper() == 'WEEK' %}
        ROUND((TRUNC(CAST({{ second_date }} AS DATE), 'DAY') - TRUNC(CAST({{ first_date }} AS DATE), 'DAY'))/7)
    {% elif datepart.upper() == 'DAY' %}
        ROUND(TRUNC(CAST({{ second_date }} AS DATE), 'DD') - TRUNC(CAST({{ first_date }} AS DATE), 'DD'))
    {% elif datepart.upper() == 'HOUR' %}
        ROUND((TRUNC(CAST({{ second_date }} AS DATE), 'HH') - TRUNC(CAST({{ first_date }} AS DATE), 'HH'))*24)
    {% elif datepart.upper() == 'MINUTE' %}
        ROUND((TRUNC(CAST({{ second_date }} AS DATE), 'MI') - TRUNC(CAST({{ first_date }} AS DATE), 'MI'))*24*60)
    {% elif datepart.upper() == 'SECOND' %}
        EXTRACT(DAY FROM (CAST({{ second_date }} AS TIMESTAMP) - CAST({{ first_date }} AS TIMESTAMP)))*24*60*60
        +EXTRACT(HOUR FROM (CAST({{ second_date }} AS TIMESTAMP) - CAST({{ first_date }} AS TIMESTAMP)))*60*60
        +EXTRACT(MINUTE FROM (CAST({{ second_date }} AS TIMESTAMP) - CAST({{ first_date }} AS TIMESTAMP)))*60
        +EXTRACT(SECOND FROM (CAST({{ second_date }} AS TIMESTAMP) - CAST({{ first_date }} AS TIMESTAMP)))
    {% endif %}
{% endmacro %}
