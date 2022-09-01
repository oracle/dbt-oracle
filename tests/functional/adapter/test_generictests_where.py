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

from dbt.tests.adapter.basic.test_generic_tests import BaseGenericTests
from dbt.tests.adapter.basic.files import (
    seeds_base_csv,
    base_view_sql,
    base_table_sql,
    schema_base_yml,
)

generic_test_seed_yml = """
version: 2
models:
  - name: base
    columns:
     - name: id
       tests:
         - not_null:
             config:
               where: "name = 'Easton'"
"""

generic_test_view_yml = """
version: 2
models:
  - name: view_model
    columns:
     - name: id
       tests:
         - not_null:
             config:
               where: "name = 'Easton'"
"""

generic_test_table_yml = """
version: 2
models:
  - name: table_model
    columns:
     - name: id
       tests:
         - not_null:
             config:
               where: "name = 'Easton'"
"""


class TestGenericTestsOracle(BaseGenericTests):

    @pytest.fixture(scope="class")
    def seeds(self):
        return {
            "base.csv": seeds_base_csv,
            "schema.yml": generic_test_seed_yml,
        }

    @pytest.fixture(scope="class")
    def models(self):
        return {
            "view_model.sql": base_view_sql,
            "table_model.sql": base_table_sql,
            "schema.yml": schema_base_yml,
            "schema_view.yml": generic_test_view_yml,
            "schema_table.yml": generic_test_table_yml,
        }
