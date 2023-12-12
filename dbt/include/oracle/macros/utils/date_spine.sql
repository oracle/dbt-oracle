{% macro oracle__get_intervals_between(start_date, end_date, datepart) -%}
    {%- call statement('get_intervals_between', fetch_result=True) %}

        select {{ dbt.datediff(start_date, end_date, datepart) }} from dual

    {%- endcall -%}

    {%- set value_list = load_result('get_intervals_between') -%}

    {%- if value_list and value_list['data'] -%}
        {%- set values = value_list['data'] | map(attribute=0) | list %}
        {{ return(values[0]) }}
    {%- else -%}
        {{ return(1) }}
    {%- endif -%}

{%- endmacro %}

{% macro oracle__date_spine_all_periods(datepart, start_date, end_date) %}
   select (
            {{
                dbt.dateadd(
                    datepart,
                    "row_number() over (order by 1) - 1",
                    start_date
                )
            }}
        ) as date_{{datepart}}
        from ({{dbt.generate_series(
            dbt.get_intervals_between(start_date, end_date, datepart)
        )}})
{% endmacro %}

{% macro oracle__date_spine(datepart, start_date, end_date) %}

    {# call as follows:

    date_spine(
        "day",
        "to_date('01/01/2016', 'mm/dd/yyyy')",
        "dbt.dateadd(week, 1, current_date)"
    ) #}

    select *
    from ({{oracle__date_spine_all_periods(datepart, start_date, end_date)}})
    where date_{{datepart}} <= {{ end_date }}

{% endmacro %}
