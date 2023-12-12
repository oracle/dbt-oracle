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
from dbt.tests.adapter.utils.fixture_generate_series import (
    models__test_generate_series_sql,
    models__test_generate_series_yml,
)

models__test_generate_series_sql = """
with generated_numbers as (
    {{ dbt.generate_series(10) }}
), expected_numbers as (
    select 1 as expected from dual
    union all
    select 2 as expected from dual
    union all
    select 3 as expected from dual
    union all
    select 4 as expected from dual
    union all
    select 5 as expected from dual
    union all
    select 6 as expected from dual
    union all
    select 7 as expected from dual
    union all
    select 8 as expected from dual
    union all
    select 9 as expected from dual
    union all
    select 10 as expected from dual
), joined as (
    select
        generated_numbers.generated_number,
        expected_numbers.expected
    from generated_numbers
    left join expected_numbers on generated_numbers.generated_number = expected_numbers.expected
)

SELECT * from joined
"""

class BaseGenerateSeries(BaseUtils):
    @pytest.fixture(scope="class")
    def models(self):
        return {
            "test_generate_series.yml": models__test_generate_series_yml,
            "test_generate_series.sql": self.interpolate_macro_namespace(
                models__test_generate_series_sql, "generate_series"
            ),
        }


class TestGenerateSeries(BaseGenerateSeries):
    pass
