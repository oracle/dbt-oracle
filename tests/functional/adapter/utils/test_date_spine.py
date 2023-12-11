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

