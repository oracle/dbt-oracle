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

{% macro oracle__dateadd(datepart, interval, from_date_or_timestamp) %}
    {%- set single_quote = "\'" -%}
    {%- set D2S_INTERVAL_UNITS = ['DAY', 'HOUR', 'MINUTE', 'SECOND'] -%}
    {%- set M2Y_INTERVAL_UNITS = ['YEAR','MONTH'] -%}
    {%- if datepart.upper() in D2S_INTERVAL_UNITS -%}
        {{ from_date_or_timestamp }} + NUMTODSINTERVAL({{ interval }}, {{single_quote ~ datepart ~ single_quote}})
    {%- elif datepart.upper() in M2Y_INTERVAL_UNITS -%}
        {{ from_date_or_timestamp }} + NUMTOYMINTERVAL({{ interval }}, {{single_quote ~ datepart ~ single_quote}})
    {%- elif datepart.upper() == 'QUARTER' -%}
        ADD_MONTHS({{ from_date_or_timestamp }}, 3*{{ interval }})
    {% elif datepart.upper() == 'WEEK' %}
        {{ from_date_or_timestamp }} + 7*{{ interval }}
    {%- endif -%}
{% endmacro %}
