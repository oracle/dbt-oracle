"""
Copyright (c) 2023, Oracle and/or its affiliates.

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

     https://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
"""
import pytest

import dbt.tests.adapter.constraints.fixtures

# model columns data types different to schema definitions
my_model_data_type_sql = """
{{{{
  config(
    materialized = "table"
  )
}}}}

select
  {sql_value} as wrong_data_type_column_name from dual
"""
dbt.tests.adapter.constraints.fixtures.my_model_data_type_sql = my_model_data_type_sql

my_model_wrong_order_sql = """
{{
  config(
    materialized = "table"
  )
}}

select
  'blue' as color,
  1 as id,
  TO_DATE('2019-01-01', 'YYYY-MM-DD') as date_day
  from dual
"""

my_model_wrong_name_sql = """
{{
  config(
    materialized = "table"
  )
}}

select
  'blue' as color,
  1 as error,
  TO_DATE('2019-01-01', 'YYYY-MM-DD') as date_day
  from dual
"""

my_model_view_wrong_order_sql = """
{{
  config(
    materialized = "view"
  )
}}

select
  'blue' as color,
  1 as id,
  TO_DATE('2019-01-01', 'YYYY-MM-DD') as date_day
  from dual
"""

my_model_view_wrong_name_sql = """
{{
  config(
    materialized = "view"
  )
}}

select
  'blue' as color,
  1 as error,
  TO_DATE('2019-01-01', 'YYYY-MM-DD') as date_day
  from dual
"""

my_model_incremental_wrong_order_sql = """
{{
  config(
    materialized = "incremental",
    on_schema_change='append_new_columns'
  )
}}

select
  'blue' as color,
  1 as id,
  TO_DATE('2019-01-01', 'YYYY-MM-DD') as date_day
  from dual
"""

my_model_incremental_wrong_name_sql = """
{{
  config(
    materialized = "incremental",
    on_schema_change='append_new_columns'
  )
}}

select
  'blue' as color,
  1 as error,
  TO_DATE('2019-01-01', 'YYYY-MM-DD') as date_day
  from dual
"""

my_model_sql = """
{{
  config(
    materialized = "table"
  )
}}

select
  1 as id,
  'blue' as color,
  TO_DATE('2019-01-01', 'YYYY-MM-DD') as date_day
  from dual
"""

# model breaking constraints
my_model_with_nulls_sql = """
{{
  config(
    materialized = "table"
  )
}}

select
  -- null value for 'id'
  cast(null as {{ dbt.type_int() }}) as id,
  -- change the color as well (to test rollback)
  'red' as color,
  TO_DATE('2019-01-01', 'YYYY-MM-DD') as date_day
  from dual
"""

my_incremental_model_sql = """
{{
  config(
    materialized = "incremental",
    on_schema_change='append_new_columns'
  )
}}

select
  1 as id,
  'blue' as color,
  TO_DATE('2019-01-01', 'YYYY-MM-DD') as date_day
  from dual
"""

my_model_incremental_with_nulls_sql = """
{{
  config(
    materialized = "incremental",
    on_schema_change='append_new_columns'  )
}}

select
  -- null value for 'id'
  cast(null as {{ dbt.type_int() }}) as id,
  -- change the color as well (to test rollback)
  'red' as color,
  TO_DATE('2019-01-01', 'YYYY-MM-DD') as date_day
  from dual
"""

model_schema_yml = """
version: 2
models:
  - name: my_model
    config:
      contract:
        enforced: true
    columns:
      - name: id
        quote: true
        data_type: integer
        description: hello
        constraints:
          - type: not_null
          - type: primary_key
          - type: check
            expression: id > 0
        tests:
          - unique
      - name: color
        data_type: char
      - name: date_day
        data_type: date
  - name: my_model_error
    config:
      contract:
        enforced: true
    columns:
      - name: id
        data_type: integer
        description: hello
        constraints:
          - type: not_null
          - type: primary_key
          - type: check
            expression: (id > 0)
        tests:
          - unique
      - name: color
        data_type: char
      - name: date_day
        data_type: date
  - name: my_model_wrong_order
    config:
      contract:
        enforced: true
    columns:
      - name: id
        data_type: integer
        description: hello
        constraints:
          - type: not_null
          - type: primary_key
          - type: check
            expression: (id > 0)
        tests:
          - unique
      - name: color
        data_type: char
      - name: date_day
        data_type: date
  - name: my_model_wrong_name
    config:
      contract:
        enforced: true
    columns:
      - name: id
        data_type: integer
        description: hello
        constraints:
          - type: not_null
          - type: primary_key
          - type: check
            expression: (id > 0)
        tests:
          - unique
      - name: color
        data_type: char
      - name: date_day
        data_type: date
"""

constrained_model_schema_yml = """
version: 2
models:
  - name: my_model
    config:
      contract:
        enforced: true
    constraints:
      - type: check
        expression: id > 0
      - type: primary_key
        columns: [ id ]
      - type: unique
        columns: [ color, date_day ]
        name: strange_uniqueness_requirement
    columns:
      - name: id
        quote: true
        data_type: integer
        description: hello
        constraints:
          - type: not_null
        tests:
          - unique
      - name: color
        data_type: char
      - name: date_day
        data_type: date
"""
