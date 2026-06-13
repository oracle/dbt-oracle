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

from dbt.tests.adapter.incremental.test_incremental_microbatch import BaseMicrobatch


class TestMicrobatch(BaseMicrobatch):
    @pytest.fixture(scope="class")
    def input_model_sql(self) -> str:
        return """
{{ config(materialized='table', event_time='event_time') }}
select 1 as id, TIMESTAMP '2020-01-01 00:00:00' as event_time from dual
union all
select 2 as id, TIMESTAMP '2020-01-02 00:00:00' as event_time from dual
union all
select 3 as id, TIMESTAMP '2020-01-03 00:00:00' as event_time from dual
"""

    @pytest.fixture(scope="class")
    def insert_two_rows_sql(self, project) -> str:
        test_schema_relation = project.adapter.Relation.create(
            database=project.database, schema=project.test_schema
        )
        return f"""
insert all
  into {test_schema_relation}.input_model (id, event_time)
    values (4, TIMESTAMP '2020-01-04 00:00:00')
  into {test_schema_relation}.input_model (id, event_time)
    values (5, TIMESTAMP '2020-01-05 00:00:00')
select 1 from dual
"""
