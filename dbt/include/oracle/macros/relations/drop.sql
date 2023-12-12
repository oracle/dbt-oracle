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
     {%- else -%}
     EXECUTE IMMEDIATE 'DROP {{ relation.type }} {{ relation }} cascade constraint';
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
