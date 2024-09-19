{#
 Copyright (c) 2024, Oracle and/or its affiliates.
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
{%- macro oracle__get_drop_sql(relation) -%}
    DECLARE
     dne_942    EXCEPTION;
     PRAGMA EXCEPTION_INIT(dne_942, -942);
     attempted_ddl_on_in_use_GTT EXCEPTION;
     pragma EXCEPTION_INIT(attempted_ddl_on_in_use_GTT, -14452);
     mv_dne_12003 EXCEPTION;
     PRAGMA EXCEPTION_INIT(mv_dne_12003, -12003);
  BEGIN
     SAVEPOINT start_transaction;
     {%- if relation.is_materialized_view -%}
     EXECUTE IMMEDIATE '{{ oracle__drop_materialized_view(relation) }}';
     {%- elif relation.is_table -%}
     EXECUTE IMMEDIATE 'DROP table {{ relation }} cascade constraints purge';
     {%- else -%}
     EXECUTE IMMEDIATE 'DROP {{ relation.type }} {{ relation }} cascade constraints';
     {%- endif -%}
     COMMIT;
  EXCEPTION
     WHEN attempted_ddl_on_in_use_GTT THEN
        NULL; -- if it its a global temporary table, leave it alone.
     WHEN dne_942 THEN
        NULL;
     WHEN mv_dne_12003 THEN
        NULL;
  END;
{%- endmacro -%}
