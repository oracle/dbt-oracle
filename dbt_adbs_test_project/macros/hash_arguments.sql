{% macro hash_arguments(args) -%}
    ORA_HASH({%- for arg in args -%}
        coalesce(cast({{ arg }} as varchar(50) ), '')
        {% if not loop.last %} || '|' || {% endif %}
    {%- endfor -%})
{%- endmacro %}