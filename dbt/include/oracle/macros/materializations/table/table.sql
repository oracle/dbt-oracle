{#
 Copyright (c) 2022, Oracle and/or its affiliates.
 Copyright 2021 dbt Labs, Inc.

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
{% materialization table, adapter='oracle' %}
  {% set identifier = model['alias'] %}
  {% set tmp_identifier = model['name'] + '__dbt_tmp' %}
  {% set backup_identifier = model['name'] + '__dbt_backup' %}
  {% set old_relation = adapter.get_relation(database=database, schema=schema, identifier=identifier) %}
  {% set target_relation = api.Relation.create(identifier=identifier,
                                                schema=schema,
                                                database=database,
                                                type='table') %}
  {% set intermediate_relation = api.Relation.create(identifier=tmp_identifier,
                                                      schema=schema,
                                                      database=database,
                                                      type='table') %}
  -- the intermediate_relation should not already exist in the database; get_relation
  -- will return None in that case. Otherwise, we get a relation that we can drop
  -- later, before we try to use this name for the current operation
  {% set preexisting_intermediate_relation = adapter.get_relation(identifier=tmp_identifier,
                                                                   schema=schema,
                                                                   database=database) %}
  /*
      See ../view/view.sql for more information about this relation.
  */
  {% set backup_relation_type = 'table' if old_relation is none else old_relation.type %}
  {% set backup_relation = api.Relation.create(identifier=backup_identifier,
                                                schema=schema,
                                                database=database,
                                                type=backup_relation_type) %}
  -- as above, the backup_relation should not already exist
  {% set preexisting_backup_relation = adapter.get_relation(identifier=backup_identifier,
                                                             schema=schema,
                                                             database=database) %}


    {% do log("Preexisting intermediate relation=" ~ preexisting_intermediate_relation) %}
    {% do log("Preexisting backup relation=" ~ preexisting_backup_relation) %}


  -- drop the temp relations if they exist already in the database
  {{ drop_relation_if_exists(preexisting_intermediate_relation) }}
  {{ drop_relation_if_exists(preexisting_backup_relation) }}

  {{ run_hooks(pre_hooks, inside_transaction=False) }}

  -- `BEGIN` happens here:
  {{ run_hooks(pre_hooks, inside_transaction=True) }}

  -- build model
  {% call statement('main') %}
    {{ create_table_as(False, intermediate_relation, sql) }}
  {%- endcall %}

  -- cleanup
  {% if old_relation is not none %}
      {% if old_relation.is_view %}
            {% do adapter.drop_relation(old_relation) %}
      {% else %}
            {% do adapter.rename_relation(old_relation, backup_relation) %}
      {% endif %}
  {% endif %}

  {{ adapter.rename_relation(intermediate_relation, target_relation) }}

  {% do create_indexes(target_relation) %}

  {{ run_hooks(post_hooks, inside_transaction=True) }}

  {% do persist_docs(target_relation, model) %}

  -- `COMMIT` happens here
  {{ adapter.commit() }}

  -- finally, drop the existing/backup relation after the commit
  {{ drop_relation_if_exists(backup_relation) }}

  {{ run_hooks(post_hooks, inside_transaction=False) }}

  {{ return({'relations': [target_relation]}) }}
{% endmaterialization %}
