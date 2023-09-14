{% macro oracle__refresh_materialized_view(relation) -%}
  BEGIN
   DBMS_MVIEW.REFRESH('{{ relation }}');
  END;
{%- endmacro %}

{% macro oracle__drop_materialized_view(relation) -%}
  DROP MATERIALIZED VIEW {{ relation }}
{%- endmacro %}

{% macro oracle__get_replace_materialized_view_as_sql(relation, sql, existing_relation, backup_relation, intermediate_relation) %}
    {{ oracle__drop_relation(existing_relation) }}
    {{ oracle__get_create_materialized_view_as_sql(relation, sql) }}
{% endmacro %}

{% macro oracle__get_create_materialized_view_as_sql(relation, sql) %}
    {%- set materialized_view = relation.from_runtime_config(config) -%}
    create materialized view {{ relation }}
        BUILD {{ materialized_view.build_mode }}
        REFRESH {{ materialized_view.refresh_method }} ON {{ materialized_view.refresh_mode }}
        {{ materialized_view.query_rewrite }} QUERY REWRITE
        AS {{ materialized_view.query }}
{% endmacro %}

{% macro oracle__get_alter_materialized_view_as_sql(
    relation,
    configuration_changes,
    sql,
    existing_relation,
    backup_relation,
    intermediate_relation
) %}

    -- apply a full refresh immediately if needed
    {% if configuration_changes.requires_full_refresh %}

        {{ get_replace_materialized_view_as_sql(relation, sql, existing_relation, backup_relation, intermediate_relation) }}

    -- otherwise apply individual changes as needed
    {% else %}

        {%- set refresh_method = configuration_changes.refresh_method -%}
        {%- set refresh_mode = configuration_changes.refresh_mode -%}
        {%- set build_mode = configuration_changes.build_mode -%}
        {%- set query_rewrite = configuration_changes.query_rewrite -%}

        ALTER MATERIALIZED VIEW {{ relation }}
        BUILD {{ build_mode.context }}
        REFRESH {{ refresh_method.context }} ON {{ refresh_mode.context }}
        {{ query_rewrite.context }} QUERY REWRITE

    {%- endif -%}

{% endmacro %}

{% macro oracle__get_materialized_view_configuration_changes(existing_relation, new_config) %}
    {% set _existing_materialized_view = oracle__describe_materialized_view_config(existing_relation) %}
    {% set _configuration_changes = existing_relation.materialized_view_config_changeset(_existing_materialized_view, new_config) %}
    {% do return(_configuration_changes) %}
{% endmacro %}


{% macro oracle__describe_materialized_view_config(relation) -%}
    {%- set _materialized_view_sql -%}
       SELECT query,
              owner,
              mview_name,
              rewrite_enabled,
              refresh_mode,
              refresh_method,
              build_mode,
              fast_refreshable,
              last_refresh_date,
              compile_state,
              last_refresh_type
       FROM sys.all_mviews
       WHERE mview_name = '{{ relation.identifier }}'
    {%- endset %}
    {% set _materialized_view = run_query(_materialized_view_sql) %}
    {% do return({'materialized_view': _materialized_view}) %}
{%- endmacro %}

