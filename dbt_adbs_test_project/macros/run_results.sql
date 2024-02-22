{% macro fetch_run_results(model) %}
    {% if model.config.materialized == 'table' %}
        SELECT COUNT(*) FROM {{model.schema}}.{{model.name}}
    {% endif %}
{%- endmacro -%}