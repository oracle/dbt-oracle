# Macros

Macros are reusable SQL, which can be invoked using `dbt run-operation` commands

## Demo Multiple statements

This addresses `ORA-00933: SQL command not properly ended` which was raised in https://github.com/techindicium/dbt-oracle/issues/26

```sql
{% macro demo_multiple_statements() -%}
    {%- call statement('demo_multiple_statements') -%}
        DECLARE
            p_id     NUMBER(4) := 412;
            p_amount NUMBER(7, 2) := 1233.00;
            sql_stmt VARCHAR2(200);
        BEGIN
            EXECUTE IMMEDIATE 'CREATE TABLE product (id NUMBER, amt NUMBER)';
            sql_stmt := 'INSERT into product values (:1, :2)';
            EXECUTE IMMEDIATE  sql_stmt USING p_id, p_amount;
            EXECUTE IMMEDIATE 'DELETE FROM product WHERE id = :num' USING p_id;
            EXECUTE IMMEDIATE 'DROP TABLE product';
        END;
    {%- endcall -%}
{% endmacro %}
```

Invoke the macro operation using `dbt run-operation` command from the project root directory

```bash
dbt --debug run-operation demo_multiple_statements --profiles-dir ./
```

The following SQL is run

```sql
DECLARE
        p_id     NUMBER(4) := 412;
        p_amount NUMBER(7, 2) := 1233.00;
        sql_stmt VARCHAR2(200);
BEGIN
        EXECUTE IMMEDIATE 'CREATE TABLE product (id NUMBER, amt NUMBER)';
        sql_stmt := 'INSERT into product values (:1, :2)';
        EXECUTE IMMEDIATE  sql_stmt USING p_id, p_amount;
        EXECUTE IMMEDIATE 'DELETE FROM product WHERE id = :num' USING p_id;
        EXECUTE IMMEDIATE 'DROP TABLE product';
END;

```
