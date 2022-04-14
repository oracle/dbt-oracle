{#
 Copyright (c) 2022, Oracle and/or its affiliates.

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
