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
{% materialization incremental, adapter='oracle', supported_languages=['sql', 'python'] %}

  {% set unique_key = config.get('unique_key') %}
  {% set full_refresh_mode = should_full_refresh() %}
  {%- set language = model['language'] -%}
  {% set target_relation = this.incorporate(type='table') %}
  {% set existing_relation = load_relation(this) %}
  {% set tmp_relation = make_temp_relation(this) %}
  {% set on_schema_change = incremental_validate_on_schema_change(config.get('on_schema_change'), default='ignore') %}
  {% set  grant_config = config.get('grants') %}

  {{ run_hooks(pre_hooks, inside_transaction=False) }}

  -- `BEGIN` happens here:
  {{ run_hooks(pre_hooks, inside_transaction=True) }}

  {% set to_drop = [] %}
  {% if existing_relation is none %}
      {% set build_sql = create_table_as(False, target_relation, sql, language) %}
  {% elif existing_relation.is_view or full_refresh_mode %}
      {#-- Make sure the backup doesn't exist so we don't encounter issues with the rename below #}
      {% set backup_identifier = existing_relation.identifier ~ "__dbt_backup" %}
      {% set backup_relation = existing_relation.incorporate(path={"identifier": backup_identifier}) %}
      {% do adapter.drop_relation(backup_relation) %}
      {% if existing_relation.is_view %}
            {% do adapter.drop_relation(existing_relation) %}
      {% else %}
            {% do adapter.rename_relation(existing_relation, backup_relation) %}
      {% endif %}
      {% set build_sql = create_table_as(False, target_relation, sql, language) %}
      {% do to_drop.append(backup_relation) %}
  {% else %}
      {% set tmp_relation = make_temp_relation(target_relation) %}
      {% do to_drop.append(tmp_relation) %}
      {% call statement("make_tmp_relation", language=language) %}
        {{create_table_as(True, tmp_relation, sql, language)}}
      {% endcall %}
      {#-- After this language should be SQL --#}
      {% set language = 'sql' %}
      {% do adapter.expand_target_column_types(
             from_relation=tmp_relation,
             to_relation=target_relation) %}
      {% set dest_columns = process_schema_changes(on_schema_change, tmp_relation, existing_relation) %}
      {% if not dest_columns %}
        {% set dest_columns = adapter.get_columns_in_relation(existing_relation) %}
      {% endif %}

      {#-- Get the incremental_strategy, the macro to use for the strategy, and build the sql --#}
      {% set incremental_strategy = config.get('incremental_strategy') or 'default' %}
      {% set incremental_predicates = config.get('predicates', none) or config.get('incremental_predicates', none) %}
      {% set strategy_sql_macro_func = adapter.get_incremental_strategy_macro(context, incremental_strategy) %}
      {% set strategy_arg_dict = ({'target_relation': target_relation, 'temp_relation': tmp_relation, 'unique_key': unique_key, 'dest_columns': dest_columns, 'incremental_predicates': incremental_predicates }) %}
      {% set build_sql = strategy_sql_macro_func(strategy_arg_dict) %}

  {% endif %}

  {% call statement("main", language=language) %}
      {{ build_sql }}
  {% endcall %}

  {% do persist_docs(target_relation, model) %}

  {{ run_hooks(post_hooks, inside_transaction=True) }}

  -- `COMMIT` happens here
  {% do adapter.commit() %}

  {% for rel in to_drop %}
      {% do adapter.truncate_relation(rel) %}
      {% do adapter.drop_relation(rel) %}
  {% endfor %}

  {{ run_hooks(post_hooks, inside_transaction=False) }}

  {% set should_revoke = should_revoke(existing_relation.is_table, full_refresh_mode) %}
  {% do apply_grants(target_relation, grant_config, should_revoke=should_revoke) %}

  {{ return({'relations': [target_relation]}) }}

{%- endmaterialization %}
