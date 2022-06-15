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
{% macro oracle__get_catalog(information_schema, schemas) -%}

  {%- call statement('catalog', fetch_result=True) -%}
    {#
      If the user has multiple databases set and the first one is wrong, this will fail.
      But we won't fail in the case where there are multiple quoting-difference-only dbs, which is better.
    #}
    {% set database = information_schema.database %}
    {% if database == 'None' or database is undefined or database is none %}
      {% set database = get_database_name() %}
    {% endif %}
    {{ adapter.verify_database(database) }}

    with columns as (
            select
                SYS_CONTEXT('userenv', 'DB_NAME') table_catalog,
                owner table_schema,
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
          ),
          tables as
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
                 select SYS_CONTEXT('userenv', 'DB_NAME'),
                   owner,
                   view_name,
                   'VIEW'
                 from sys.all_views
          )
          select
              tables.table_catalog as "table_database",
              tables.table_schema as "table_schema",
              tables.table_name as "table_name",
              tables.table_type as "table_type",
              all_tab_comments.comments as "table_comment",
              columns.column_name as "column_name",
              ordinal_position as "column_index",
              case
                when data_type like '%CHAR%'
                then data_type || '(' || cast(char_length as varchar(10)) || ')'
                else data_type
              end as "column_type",
              all_col_comments.comments as "column_comment",
              tables.table_schema as "table_owner"
          from tables
          inner join columns on columns.table_catalog = tables.table_catalog
            and columns.table_schema = tables.table_schema
            and columns.table_name = tables.table_name
          left join all_tab_comments
            on all_tab_comments.owner = tables.table_schema
              and all_tab_comments.table_name = tables.table_name
          left join all_col_comments
            on all_col_comments.owner = columns.table_schema
              and all_col_comments.table_name = columns.table_name
              and all_col_comments.column_name = columns.column_name
          where (
              {%- for schema in schemas -%}
                tables.table_schema = upper('{{ schema }}'){%- if not loop.last %} or {% endif -%}
              {%- endfor -%}
            )
          order by
              tables.table_schema,
              tables.table_name,
              ordinal_position
  {%- endcall -%}

  {{ return(load_result('catalog').table) }}

{%- endmacro %}
