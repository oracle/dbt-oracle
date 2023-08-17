{% macro oracle__refresh_materialized_view(relation) -%}
  BEGIN
   DBMS_MVIEW.REFRESH('{{ relation }}');
  END;
{%- endmacro %}

{% macro oracle__drop_materialized_view(relation) -%}
  DROP MATERIALIZED VIEW {{ relation }}
{%- endmacro %}

{% macro oracle_get_materialized_view_config(relation) -%}
    {% call statement('get_materialized_view_config', fetch_result=True) -%}
       SELECT query,
              rewrite_enabled,
              refresh_mode,
              refresh_method,
              build_mode,
              fast_refreshable,
              last_refresh_type
       from sys.all_mviews
       where mview_name = '{{ relation }}'
    {%- endcall %}
    {{ return(load_result('get_materialized_view_config').table) }}
{%- endmacro %}

