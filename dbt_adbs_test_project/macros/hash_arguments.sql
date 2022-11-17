{% macro hash_arguments(args) -%}
    ORA_HASH({%- for arg in args -%}
        coalesce(cast({{ arg }} as varchar(50) ), '')
        {% if not loop.last %} || '|' || {% endif %}
    {%- endfor -%})
{%- endmacro %}

{% macro oracle__snapshot_hash_arguments(args) -%}
    STANDARD_HASH({%- for arg in args -%}
        coalesce(cast({{ arg }} as varchar(4000) ), '')
        {% if not loop.last %} || '|' || {% endif %}
    {%- endfor -%}, 'SHA256')
{%- endmacro %}