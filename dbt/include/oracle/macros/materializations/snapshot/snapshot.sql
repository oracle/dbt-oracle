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

{#
    Add new columns to the table if applicable
#}
{% macro create_columns(relation, columns) %}
  {{ adapter.dispatch('create_columns')(relation, columns) }}
{% endmacro %}

{% macro default__create_columns(relation, columns) %}
  {% for column in columns %}
    {% call statement() %}
      alter table {{ relation }} add column "{{ column.name }}" {{ column.data_type }};
    {% endcall %}
  {% endfor %}
{% endmacro %}


{% macro post_snapshot(staging_relation) %}
  {{ adapter.dispatch('post_snapshot')(staging_relation) }}
{% endmacro %}

{% macro oracle__post_snapshot(staging_relation) %}
    {% do adapter.truncate_relation(staging_relation) %}
    {% do adapter.drop_relation(staging_relation) %}
{% endmacro %}


{% macro oracle__snapshot_staging_table(strategy, source_sql, target_relation) -%}

    {% set columns = config.get('snapshot_table_column_names') or get_snapshot_table_column_names() %}
    {% if strategy.hard_deletes == 'new_record' %}
        {% set new_scd_id = snapshot_hash_arguments([columns.dbt_scd_id, snapshot_get_time()]) %}
    {% endif %}

    with snapshot_query as (

        {{ source_sql }}

    ),

    snapshotted_data as (

        select {{ target_relation }}.*,
            {{ unique_key_fields(strategy.unique_key) }}
        from {{ target_relation }}
        where
            {% if config.get('dbt_valid_to_current') %}
                {% set source_unique_key = columns.dbt_valid_to | trim %}
                {% set target_unique_key = config.get('dbt_valid_to_current') | trim %}
                ( {{ equals(source_unique_key, target_unique_key) }} or {{ source_unique_key }} is null )
            {% else %}
                {{ columns.dbt_valid_to }} is null
            {% endif %}
    ),

    insertions_source_data as (

        select
            snapshot_query.*,
            {{ unique_key_fields(strategy.unique_key) }},
            {{ strategy.updated_at }} as {{ columns.dbt_updated_at }},
            {{ strategy.updated_at }} as {{ columns.dbt_valid_from }},
            {{ oracle__get_dbt_valid_to_current(strategy, columns) }},
            {{ strategy.scd_id }} as {{ columns.dbt_scd_id }}

        from snapshot_query
    ),

    updates_source_data as (

        select
            snapshot_query.*,
            {{ unique_key_fields(strategy.unique_key) }},
            {{ strategy.updated_at }} as {{ columns.dbt_updated_at }},
            {{ strategy.updated_at }} as {{ columns.dbt_valid_from }},
            {{ strategy.updated_at }} as {{ columns.dbt_valid_to }}

        from snapshot_query
    ),

    {%- if strategy.hard_deletes == 'invalidate' or strategy.hard_deletes == 'new_record' %}

    deletes_source_data as (

        select
            snapshot_query.*,
            {{ unique_key_fields(strategy.unique_key) }}
        from snapshot_query
    ),
    {% endif %}

    insertions as (

        select
            'insert' as dbt_change_type,
            source_data.*
            {%- if strategy.hard_deletes == 'new_record' -%}
            ,'False' as {{ columns.dbt_is_deleted }}
            {%- endif %}

        from insertions_source_data source_data
        left outer join snapshotted_data
        on {{ unique_key_join_on(strategy.unique_key, "snapshotted_data", "source_data") }}
        where {{ unique_key_is_null(strategy.unique_key, "snapshotted_data") }}
            or ({{ unique_key_is_not_null(strategy.unique_key, "snapshotted_data") }} and ({{ strategy.row_changed }})

        )

    ),

    updates as (

        select
            'update' as dbt_change_type,
            source_data.*,
            snapshotted_data.{{ columns.dbt_scd_id }}
         {%- if strategy.hard_deletes == 'new_record' -%}
            , snapshotted_data.{{ columns.dbt_is_deleted }}
          {%- endif %}

        from updates_source_data source_data
        join snapshotted_data
            on {{ unique_key_join_on(strategy.unique_key, "snapshotted_data", "source_data") }}
        where (
            {{ strategy.row_changed }}
        )
    )

    {%- if strategy.hard_deletes == 'invalidate' or strategy.hard_deletes == 'new_record' -%}
    ,

    deletes as (

        select
            'delete' as dbt_change_type,
            source_data.*,
            {{ snapshot_get_time() }} as {{ columns.dbt_valid_from }},
            {{ snapshot_get_time() }} as {{ columns.dbt_updated_at }},
            {{ snapshot_get_time() }} as {{ columns.dbt_valid_to }},
            snapshotted_data.{{ columns.dbt_scd_id }}
          {%- if strategy.hard_deletes == 'new_record' -%}
            , snapshotted_data.{{ columns.dbt_is_deleted }}
          {%- endif %}

        from snapshotted_data
        left join deletes_source_data source_data
        on {{ unique_key_join_on(strategy.unique_key, "snapshotted_data", "source_data") }}
            where {{ unique_key_is_null(strategy.unique_key, "source_data") }}
    )
    {%- endif %}

    {%- if strategy.hard_deletes == 'new_record' %}
        {% set source_sql_cols = get_column_schema_from_query(source_sql) %}
    ,
    deletion_records as (

        select
            'insert' as dbt_change_type,
            {%- for col in source_sql_cols -%}
            snapshotted_data.{{ adapter.quote(col.column) }},
            {% endfor -%}
            {%- if strategy.unique_key | is_list -%}
                {%- for key in strategy.unique_key -%}
            snapshotted_data.{{ key }} as dbt_unique_key_{{ loop.index }},
                {% endfor -%}
            {%- else -%}
            snapshotted_data.dbt_unique_key as dbt_unique_key,
            {% endif -%}
            {{ snapshot_get_time() }} as {{ columns.dbt_valid_from }},
            {{ snapshot_get_time() }} as {{ columns.dbt_updated_at }},
            snapshotted_data.{{ columns.dbt_valid_to }} as {{ columns.dbt_valid_to }},
            {{ new_scd_id }} as {{ columns.dbt_scd_id }},
            'True' as {{ columns.dbt_is_deleted }}
        from snapshotted_data
        left join deletes_source_data source_data
            on {{ unique_key_join_on(strategy.unique_key, "snapshotted_data", "source_data") }}
        where {{ unique_key_is_null(strategy.unique_key, "source_data") }}

    )
    {%- endif %}

    select * from insertions
    union all
    select * from updates
    {%- if strategy.hard_deletes == 'invalidate' or strategy.hard_deletes == 'new_record' %}
    union all
    select * from deletes
    {%- endif %}
    {%- if strategy.hard_deletes == 'new_record' %}
    union all
    select * from deletion_records
    {%- endif %}

{%- endmacro %}



{% macro oracle__build_snapshot_table(strategy, sql) %}
    {% set columns = config.get('snapshot_table_column_names') or get_snapshot_table_column_names() %}

    select sbq.*,
        {{ strategy.scd_id }} as {{ columns.dbt_scd_id }},
        {{ strategy.updated_at }} as {{ columns.dbt_updated_at }},
        {{ strategy.updated_at }} as {{ columns.dbt_valid_from }},
        {{ oracle__get_dbt_valid_to_current(strategy, columns) }}
    {%- if strategy.hard_deletes == 'new_record' -%}
        , 'False' as {{ columns.dbt_is_deleted }}
      {% endif -%}
    from (
        {{ sql }}
    ) sbq

{% endmacro %}


{% macro get_or_create_relation(database, schema, identifier, type) %}
  {%- set target_relation = adapter.get_relation(database=database, schema=schema, identifier=identifier) %}

  {% if target_relation %}
    {% do return([true, target_relation]) %}
  {% endif %}

  {%- set new_relation = api.Relation.create(
      database=database,
      schema=schema,
      identifier=identifier,
      type=type
  ) -%}
  {% do return([false, new_relation]) %}
{% endmacro %}

{% macro build_snapshot_staging_table(strategy, sql, target_relation) %}
    {% set tmp_relation = make_temp_relation(target_relation) %}

    {% set select = snapshot_staging_table(strategy, sql, target_relation) %}

    {% call statement('build_snapshot_staging_relation') %}
        {{ create_table_as(True, tmp_relation, select) }}
    {% endcall %}

    {% do return(tmp_relation) %}
{% endmacro %}


{% materialization snapshot, adapter='oracle' %}

  {%- set target_table = model.get('alias', model.get('name')) -%}

  {%- set strategy_name = config.get('strategy') -%}
  {%- set unique_key = config.get('unique_key') %}
  {%- set grant_config = config.get('grants') -%}
  {% set model_database = model.database %}
  {% if model_database == 'None' or model_database is undefined or model_database is none %}
    {% set model_database = get_database_name() %}
  {% endif %}

  {% if not adapter.check_schema_exists(model_database, model.schema) %}
    {% do create_schema(model.schema) %}
  {% endif %}

  {% set target_relation_exists, target_relation = get_or_create_relation(
          database=model_database,
          schema=model.schema,
          identifier=target_table,
          type='table') -%}

  {%- if not target_relation.is_table -%}
    {% do exceptions.relation_wrong_type(target_relation, 'table') %}
  {%- endif -%}


  {{ run_hooks(pre_hooks, inside_transaction=False) }}

  {{ run_hooks(pre_hooks, inside_transaction=True) }}

  {% set strategy_macro = strategy_dispatch(strategy_name) %}
  {% set strategy = strategy_macro(model, "snapshotted_data", "source_data", config, target_relation_exists) %}

  {% if not target_relation_exists %}

      {% set build_sql = build_snapshot_table(strategy, model['compiled_sql']) %}
      {% set build_or_select_sql = build_sql %}
      {% set final_sql = create_table_as(False, target_relation, build_sql) %}

  {% else %}

      {% set columns = config.get("snapshot_table_column_names") or get_snapshot_table_column_names() %}

      {{ adapter.assert_valid_snapshot_target_given_strategy(target_relation, columns, strategy) }}

      {% set build_or_select_sql = snapshot_staging_table(strategy, sql, target_relation) %}
      {% set staging_table = build_snapshot_staging_table(strategy, sql, target_relation) %}

      -- this may no-op if the database does not require column expansion
      {% do adapter.expand_target_column_types(from_relation=staging_table,
                                               to_relation=target_relation) %}

      {% set remove_columns = ['dbt_change_type', 'DBT_CHANGE_TYPE', 'dbt_unique_key', 'DBT_UNIQUE_KEY'] %}
      {% if unique_key | is_list %}
          {% for key in strategy.unique_key %}
              {{ remove_columns.append('dbt_unique_key_' + loop.index|string) }}
              {{ remove_columns.append('DBT_UNIQUE_KEY_' + loop.index|string) }}
          {% endfor %}
      {% endif %}

      {% set missing_columns = adapter.get_missing_columns(staging_table, target_relation)
                                   | rejectattr('name', 'in', remove_columns)
                                   | list %}

      {% do create_columns(target_relation, missing_columns) %}

      {% set source_columns = adapter.get_columns_in_relation(staging_table)
                                   | rejectattr('name', 'in', remove_columns)
                                   | list %}

      {% set quoted_source_columns = [] %}
      {% for column in source_columns %}
        {% do quoted_source_columns.append(column.name) %}
      {% endfor %}

      {% set final_sql = snapshot_merge_sql(
            target = target_relation,
            source = staging_table,
            insert_cols = quoted_source_columns
         )
      %}

  {% endif %}

  {{ check_time_data_types(build_or_select_sql) }}

  {% call statement('main') %}
      {{ final_sql }}
  {% endcall %}

  {% set should_revoke = should_revoke(target_relation_exists, full_refresh_mode=False) %}
  {% do apply_grants(target_relation, grant_config, should_revoke=should_revoke) %}

  {% do persist_docs(target_relation, model) %}

  {{ run_hooks(post_hooks, inside_transaction=True) }}

  {{ adapter.commit() }}

  {% if staging_table is defined %}
      {% do post_snapshot(staging_table) %}
  {% endif %}

  {{ run_hooks(post_hooks, inside_transaction=False) }}

  {{ return({'relations': [target_relation]}) }}

{% endmaterialization %}

{% macro oracle__snapshot_hash_arguments(args) -%}
    STANDARD_HASH({%- for arg in args -%}
        coalesce(cast({{ arg }} as varchar(4000) ), '')
        {% if not loop.last %} || '|' || {% endif %}
    {%- endfor -%}, 'SHA256')
{%- endmacro %}

{% macro oracle__get_dbt_valid_to_current(strategy, columns) %}
  {% set dbt_valid_to_current = config.get('dbt_valid_to_current') or "CAST(null as TIMESTAMP(9))" %}
  coalesce(nullif({{ strategy.updated_at }}, {{ strategy.updated_at }}), {{dbt_valid_to_current}})
  as {{ columns.dbt_valid_to }}
{% endmacro %}

