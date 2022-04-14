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
{% macro oracle__test_accepted_values(model, column_name, values, quote=True) %}

with all_values as (

    select distinct
        {{ column_name }} as value_field

    from {{ model.include(False, True, True) }}

),

validation_errors as (

    select
        value_field

    from all_values
    where value_field not in (
        {% for value in values -%}
            {% if quote -%}
            '{{ value }}'
            {%- else -%}
            {{ value }}
            {%- endif -%}
            {%- if not loop.last -%},{%- endif %}
        {%- endfor %}
    )
)

select * from(
    select count(*) as not_accepted_values from validation_errors
                 ) c where c.not_accepted_values != 0

{% endmacro %}

{% macro oracle__test_not_null(model, column_name) %}

select * from (
select count(*) as null_count
from {{ model.include(False, True, True) }}
where {{ column_name }} is null) c where c.null_count != 0

{% endmacro %}

{% macro oracle__test_relationships(model, column_name, to, field) %}

select * from (
select count(*) as validation_errors
from (
    select {{ column_name }} as id from {{ model }}
) child
left join (
    select {{ field }} as id from {{ to }}
) parent on parent.id = child.id
where child.id is not null
  and parent.id is null) c where c.validation_errors != 0

{% endmacro %}
