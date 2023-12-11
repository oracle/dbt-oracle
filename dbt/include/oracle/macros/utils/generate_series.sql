{% macro oracle__generate_series(upper_bound) %}
    select to_number(column_value) as generated_number from xmltable('1 to {{upper_bound}}')
{% endmacro %}
