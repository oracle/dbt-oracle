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

from dbt.tests.adapter.utils.base_utils import BaseUtils
from dbt.tests.adapter.utils.fixture_date_spine import (
    models__test_date_spine_yml,
)

models__test_date_spine_sql = """
with generated_dates as (
    {{ date_spine("day", "to_date('2023-09-01', 'YYYY-MM-DD')", "to_date('2023-09-10', 'YYYY-MM-DD')") }}
), expected_dates as (
        select to_date('2023-09-01', 'YYYY-MM-DD') as expected from dual 
        union all
        select to_date('2023-09-02', 'YYYY-MM-DD') as expected from dual 
        union all
        select to_date('2023-09-03', 'YYYY-MM-DD') as expected from dual 
        union all
        select to_date('2023-09-04', 'YYYY-MM-DD') as expected from dual
        union all
        select to_date('2023-09-05', 'YYYY-MM-DD') as expected from dual
        union all
        select to_date('2023-09-06', 'YYYY-MM-DD') as expected from dual
        union all
        select to_date('2023-09-07', 'YYYY-MM-DD') as expected from dual
        union all
        select to_date('2023-09-08', 'YYYY-MM-DD') as expected from dual
        union all
        select to_date('2023-09-09', 'YYYY-MM-DD') as expected from dual
)
select
    generated_dates.date_day,
    expected_dates.expected
from generated_dates
left join expected_dates on generated_dates.date_day = expected_dates.expected
"""


class BaseDateSpine(BaseUtils):
    @pytest.fixture(scope="class")
    def models(self):
        return {
            "test_date_spine.yml": models__test_date_spine_yml,
            "test_date_spine.sql": self.interpolate_macro_namespace(
                models__test_date_spine_sql, "date_spine"
            ),
        }


class TestDateSpine(BaseDateSpine):
    pass

