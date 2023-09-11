{%- macro random_digits(n) -%}
    {%- for _ in range(n) -%}
        {{ range(10) | random }}
    {%- endfor -%}
{%- endmacro -%}

{% macro create_index(idx_prefix, columns) %}
{%- set columns_name = columns | replace(', ', '__') | replace(',', '__') -%}
{%- set random_part = random_digits(16) -%}
{%- set index_name = idx_prefix ~ "__idx_" ~ random_part ~ "_on__" ~ columns_name -%}
{%- set sql -%}
CREATE INDEX "{{ index_name }}" ON {{ this }} ({{ columns }})
{%- endset -%}
{%- if execute -%}
    {{- log("Creating index...", info = true) -}}
    {% do run_query(sql) %}
{%- endif -%}
{%- endmacro -%}
