"""
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
"""

import pytest
from dbt.tests.util import run_dbt, get_relation_columns

# seeds/my_seed.csv
my_seed_csv = """
id,name,some_date
1,Easton,1981-05-20T06:46:51
2,Lillian,1978-09-03T18:10:33
3,Jeremiah,1982-03-11T03:59:51
4,Nolan,1976-05-06T20:21:35
""".lstrip()

# models/my_model.sql
my_model_sql = """
{{config(materialized='table')}}
select * from {{ ref('my_seed') }}
"""

# wrapper macro which calls the alter_column_type macro
alter_column_type_wrapper_macro = """
{% macro wrap_alter_column_type() %}
    {%- set relation = adapter.get_relation(database=target.database, schema=schema, identifier='my_model') -%}
    {{ return(adapter.dispatch('alter_column_type')(relation, 'name', 'CLOB')) }}
{% endmacro %}
"""


class TestAlterColumnDataTypeMacro:
    """
    Tests the macro `oracle__alter_column_type`

    """

    @pytest.fixture(scope="class")
    def seeds(self):
        return {
            "my_seed.csv": my_seed_csv,
        }

    @pytest.fixture(scope="class")
    def models(self):
        return {
            "my_model.sql": my_model_sql,
        }

    @pytest.fixture(scope="class")
    def macros(self):
        return {"wrap_alter_column_type.sql": alter_column_type_wrapper_macro}

    def test_run_macro(self, project):
        """seed, then run, then macro to alter table column datatype

        """
        results = run_dbt(['seed'])
        assert len(results) == 1

        results = run_dbt(['run'])
        assert len(results) == 1

        run_dbt(['run-operation', 'wrap_alter_column_type'])
        columns = get_relation_columns(project.adapter, 'my_model')
        expected_columns = [('ID', 'NUMBER', 0),
                            ('NAME', 'CLOB', 0),
                            ('SOME_DATE', 'TIMESTAMP(6)', 0)]
        assert expected_columns == columns


