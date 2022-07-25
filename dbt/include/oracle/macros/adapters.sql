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
{% macro oracle__get_columns_in_query(select_sql) %}
    {% call statement('get_columns_in_query', fetch_result=True, auto_begin=False) -%}
        select * from (
            {{ select_sql }}
        ) dbt_sbq_tmp
        where 1 = 0 and rownum < 1
    {% endcall %}

    {{ return(load_result('get_columns_in_query').table.columns | map(attribute='name') | list) }}
{% endmacro %}


{% macro oracle__create_schema(relation, schema_name) -%}
  {% if relation.database -%}
    {{ adapter.verify_database(relation.database) }}
  {%- endif -%}
  {%- call statement('create_schema') -%}
    -- Noop for not breaking tests, oracle
    -- schemas are actualy users, we can't
    -- create it here
    select 'a' from dual
  {%- endcall -%}
{% endmacro %}

{% macro oracle__drop_schema(schema) -%}
  {% if schema.database -%}
    {{ adapter.verify_database(schema.database) }}
  {%- endif -%}
  {%- call statement('drop_schema') -%}
    -- from https://gist.github.com/rafaeleyng/33eaef673fc4ee98a6de4f70c8ce3657
    BEGIN
    FOR cur_rec IN (SELECT object_name, object_type
                      FROM ALL_objects
                      WHERE object_type IN
                              ('TABLE',
                                'VIEW',
                                'PACKAGE',
                                'PROCEDURE',
                                'FUNCTION',
                                'SEQUENCE',
                                'TYPE',
                                'SYNONYM',
                                'MATERIALIZED VIEW'
                              )
                      AND owner = '{{ schema | upper }}')
    LOOP
        BEGIN
          IF cur_rec.object_type = 'TABLE'
          THEN
              EXECUTE IMMEDIATE    'DROP '
                                || cur_rec.object_type
                                || ' "'
                                || cur_rec.object_name
                                || '" CASCADE CONSTRAINTS';
          ELSE
              EXECUTE IMMEDIATE    'DROP '
                                || cur_rec.object_type
                                || ' "'
                                || cur_rec.object_name
                                || '"';
          END IF;
        EXCEPTION
          WHEN OTHERS
          THEN
              DBMS_OUTPUT.put_line (   'FAILED: DROP '
                                    || cur_rec.object_type
                                    || ' "'
                                    || cur_rec.object_name
                                    || '"'
                                  );
        END;
    END LOOP;
  END;
  {%- endcall -%}
{% endmacro %}

{% macro oracle__create_table_as_backup(temporary, relation, sql) -%}
  {%- set sql_header = config.get('sql_header', none) -%}

  {{ sql_header if sql_header is not none }}
  create {% if temporary -%}
    global temporary
  {%- endif %} table {{ relation.include(schema=(not temporary)) }}
  {% if temporary -%} on commit preserve rows {%- endif %}
  as
    {{ sql }}

{%- endmacro %}


{% macro oracle__create_table_as(temporary, relation, sql) -%}
  {%- set sql_header = config.get('sql_header', none) -%}

  {{ sql_header if sql_header is not none }}

  create {% if temporary -%}
    global temporary
  {%- endif %} table {{ relation.include(schema=(not temporary)) }}
  {% if temporary -%} on commit preserve rows {%- endif %}
  as
    {{ sql }}

{%- endmacro %}
{% macro oracle__create_view_as(relation, sql) -%}
  {%- set sql_header = config.get('sql_header', none) -%}

  {{ sql_header if sql_header is not none }}
  create or replace view {{ relation }} as
    {{ sql }}

{% endmacro %}

{% macro oracle__get_columns_in_relation(relation) -%}
  {% call statement('get_columns_in_relation', fetch_result=True) %}
      with columns as (
        select
            UPPER(SYS_CONTEXT('userenv', 'DB_NAME')) table_catalog,
            UPPER(owner) table_schema,
            table_name,
            column_name,
            data_type,
            data_type_mod,
            decode(data_type_owner, null, TO_CHAR(null), SYS_CONTEXT('userenv', 'DB_NAME')) domain_catalog,
            data_type_owner domain_schema,
            data_length character_maximum_length,
            data_length character_octet_length,
            data_length,
            data_precision numeric_precision,
            data_scale numeric_scale,
            nullable is_nullable,
            column_id ordinal_position,
            default_length,
            data_default column_default,
            num_distinct,
            low_value,
            high_value,
            density,
            num_nulls,
            num_buckets,
            last_analyzed,
            sample_size,
            SYS_CONTEXT('userenv', 'DB_NAME') character_set_catalog,
            'SYS' character_set_schema,
            SYS_CONTEXT('userenv', 'DB_NAME') collation_catalog,
            'SYS' collation_schema,
            character_set_name,
            char_col_decl_length,
            global_stats,
            user_stats,
            avg_col_len,
            char_length,
            char_used,
            v80_fmt_image,
            data_upgraded,
            histogram
          from sys.all_tab_columns
      )
      select
          column_name as "name",
          data_type as "type",
          char_length as "character_maximum_length",
          numeric_precision as "numeric_precision",
          numeric_scale as "numeric_scale"
      from columns
      where table_name = upper('{{ relation.identifier }}')
        {% if relation.schema %}
        and table_schema = upper('{{ relation.schema }}')
        {% endif %}
      order by ordinal_position

  {% endcall %}
  {% set table = load_result('get_columns_in_relation').table %}
  {{ return(sql_convert_columns_in_relation(table)) }}
{% endmacro %}

{% macro oracle_escape_comment(comment) -%}
  {% if comment is not string %}
    {% do exceptions.raise_compiler_error('cannot escape a non-string: ' ~ comment) %}
  {% endif %}
  {%- set start_quote = "q'<" -%}
  {%- set end_quote = ">'" -%}
  {%- if end_quote in comment -%}
    {%- do exceptions.raise_compiler_error('The string ' ~ end_quote ~ ' is not allowed in comments.') -%}
  {%- endif -%}
  {{ start_quote }}{{ comment }}{{ end_quote }}
{%- endmacro %}

{% macro oracle__alter_relation_comment(relation, comment) %}
  {% set escaped_comment = oracle_escape_comment(comment) %}
  {# "comment on table" even for views #}
  comment on table {{ relation }} is {{ escaped_comment }}
{% endmacro %}

{% macro oracle__persist_docs(relation, model, for_relation, for_columns) -%}
  {% if for_relation and config.persist_relation_docs() and model.description %}
    {% do run_query(alter_relation_comment(relation, model.description)) %}
  {% endif %}
  {% if for_columns and config.persist_column_docs() and model.columns %}
    {% set column_dict = model.columns %}
    {% for column_name in column_dict %}
      {% set comment = column_dict[column_name]['description'] %}
      {% set escaped_comment = oracle_escape_comment(comment) %}
      {% call statement('alter _column comment', fetch_result=False) -%}
        comment on column {{ relation }}.{{ column_name }} is {{ escaped_comment }}
      {%- endcall %}
    {% endfor %}
  {% endif %}
{% endmacro %}

{% macro oracle__alter_column_type(relation, column_name, new_column_type) -%}
  {#
    1. Create a new column (w/ temp name and correct type)
    2. Copy data over to it
    3. Drop the existing column (cascade!)
    4. Rename the new column to existing column
  #}
  {%- set tmp_column = column_name + "__dbt_alter" -%}

  {% call statement('alter_column_type 1', fetch_result=False) %}
    alter table {{ relation }} add {{ tmp_column }} {{ new_column_type }}
  {% endcall %}
  {% call statement('alter_column_type 2', fetch_result=False) %}
    update {{ relation  }} set {{ tmp_column }} = {{ column_name }}
  {% endcall %}
  {% call statement('alter_column_type 3', fetch_result=False) %}
    alter table {{ relation }} drop column {{ column_name }} cascade constraints
  {% endcall %}
  {% call statement('alter_column_type 4', fetch_result=False) %}
    alter table {{ relation }} rename column {{ tmp_column }} to {{ column_name }}
  {% endcall %}

{% endmacro %}

{% macro oracle__drop_relation(relation) -%}
  {% call statement('drop_relation', auto_begin=False) -%}
   DECLARE
     dne_942    EXCEPTION;
     PRAGMA EXCEPTION_INIT(dne_942, -942);
     attempted_ddl_on_in_use_GTT EXCEPTION;
     pragma EXCEPTION_INIT(attempted_ddl_on_in_use_GTT, -14452);
  BEGIN
     SAVEPOINT start_transaction;
     EXECUTE IMMEDIATE 'DROP {{ relation.type }} {{ relation }} cascade constraint';
     COMMIT;
  EXCEPTION
     WHEN attempted_ddl_on_in_use_GTT THEN
        NULL; -- if it its a global temporary table, leave it alone.
     WHEN dne_942 THEN
        NULL;
  END;
  {%- endcall %}
{% endmacro %}

{% macro oracle__truncate_relation(relation) -%}
  {#-- To avoid `ORA-01702: a view is not appropriate here` we check that the relation to be truncated is a table #}
  {% if relation.is_table %}
    {% call statement('truncate_relation') -%}
        truncate table {{ relation }}
    {%- endcall %}
  {% endif %}
{% endmacro %}

{% macro oracle__rename_relation(from_relation, to_relation) -%}
  {% call statement('rename_relation') -%}
    ALTER {{ from_relation.type }} {{ from_relation }} rename to {{ to_relation.include(schema=False) }}
  {%- endcall %}
{% endmacro %}

{% macro oracle__information_schema_name(database) -%}
  {% if database -%}
    {{ adapter.verify_database(database) }}
  {%- endif -%}
  sys
{%- endmacro %}

{% macro oracle__list_schemas(database) %}
  {% if database -%}
    {{ adapter.verify_database(database) }}
  {%- endif -%}
  {% call statement('list_schemas', fetch_result=True, auto_begin=False) -%}
     	select username as "name"
      from sys.all_users
      order by username
  {% endcall %}
  {{ return(load_result('list_schemas').table) }}
{% endmacro %}

{% macro oracle__check_schema_exists(information_schema, schema) -%}
  {% if information_schema.database -%}
    {{ adapter.verify_database(information_schema.database) }}
  {%- endif -%}
  {% call statement('check_schema_exists', fetch_result=True, auto_begin=False) %}
    select count(*) from sys.all_users where username = upper('{{ schema }}')
  {% endcall %}
  {{ return(load_result('check_schema_exists').table) }}
{% endmacro %}

{% macro oracle__list_relations_without_caching(schema_relation) %}
  {% call statement('list_relations_without_caching', fetch_result=True) -%}
    with tables as
      (select UPPER(SYS_CONTEXT('userenv', 'DB_NAME')) table_catalog,
         UPPER(owner) table_schema,
         table_name,
         case
           when iot_type = 'Y'
           then 'IOT'
           when temporary = 'Y'
           then 'TEMP'
           else 'BASE TABLE'
         end table_type
       from sys.all_tables
       union all
       select UPPER(SYS_CONTEXT('userenv', 'DB_NAME')),
         UPPER(owner),
         view_name,
         'VIEW'
       from sys.all_views
  )
  select table_catalog as "database_name"
    ,table_name as "name"
    ,table_schema as "schema_name"
    ,case table_type
      when 'BASE TABLE' then 'table'
      when 'VIEW' then 'view'
    end as "kind"
  from tables
  where table_type in ('BASE TABLE', 'VIEW')
    and table_schema = upper('{{ schema_relation.schema }}')
  {% endcall %}
  {{ return(load_result('list_relations_without_caching').table) }}
{% endmacro %}

{% macro oracle__current_timestamp() -%}
  CURRENT_TIMESTAMP
{%- endmacro %}

{% macro oracle__make_temp_relation(base_relation, suffix) %}
    {% set dt = modules.datetime.datetime.now() %}
    {% set dtstring = dt.strftime("%H%M%S") %}
    {% set tmp_identifier = 'o$pt_' ~ base_relation.identifier ~ dtstring %}
    {% set tmp_relation = base_relation.incorporate(
                                path={"identifier": tmp_identifier, "schema": None}) -%}

    {% do return(tmp_relation) %}
{% endmacro %}

{% macro get_database_name() %}
    {% set results = run_query("select SYS_CONTEXT('userenv', 'DB_NAME') FROM DUAL") %}
    {% set db_name = results.columns[0].values()[0] %}
    {{ return(db_name) }}
{% endmacro %}
