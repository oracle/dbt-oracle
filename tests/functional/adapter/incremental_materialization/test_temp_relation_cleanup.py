"""
Copyright (c) 2026, Oracle and/or its affiliates.

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

from dbt.tests.util import run_dbt


failing_incremental_sql = """
{{
    config(
        materialized='incremental',
        unique_key='id',
        on_schema_change='fail',
        contract={'enforced': true}
    )
}}

select 1 as id, cast('ok' as varchar2(10)) as required_value from dual

{% if is_incremental() %}
union all
select 2 as id, cast(null as varchar2(10)) as required_value from dual
{% endif %}
"""


failing_incremental_schema_yml = """
version: 2

models:
  - name: failing_incremental
    columns:
      - name: id
        data_type: number
      - name: required_value
        data_type: varchar2(10)
        constraints:
          - type: not_null
"""


class TestIncrementalTempRelationCleanup:
    @pytest.fixture(scope="class")
    def schema(self):
        return "test_temp_relation_cleanup"

    @pytest.fixture(scope="class")
    def models(self):
        return {
            "failing_incremental.sql": failing_incremental_sql,
            "schema.yml": failing_incremental_schema_yml,
        }

    def test_temp_relation_dropped_after_incremental_error(self, project):
        results = run_dbt(["run"])
        assert len(results) == 1

        run_dbt(["run"], expect_pass=False)

        temp_relation_count = project.run_sql(
            """
            select count(*)
            from user_tables
            where table_name like 'O$PT_FAILING_INCREMENTAL%'
            """,
            fetch="one",
        )[0]
        assert temp_relation_count == 0
