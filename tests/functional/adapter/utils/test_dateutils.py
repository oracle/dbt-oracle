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
from dbt.tests.adapter.utils.test_dateadd import BaseDateAdd
from dbt.tests.adapter.utils.test_last_day import BaseLastDay
from dbt.tests.adapter.utils.test_date_trunc import BaseDateTrunc

from dbt.tests.adapter.utils.fixture_dateadd import models__test_dateadd_yml

seeds__data_date_trunc_csv = """updated_at,day,month
2018-01-05 12:00:00,2017-12-31 00:00:00,2018-01-01 00:00:00
"""

seeds__data_dateadd_csv = """start_date,interval_length,datepart,expected
2018-01-20T01:00:00,1,day,2018-01-21T01:00:00
2018-01-20T01:00:00,1,month,2018-02-20T01:00:00
2018-01-20T01:00:00,1,year,2019-01-20T01:00:00
2018-01-20T01:00:00,1,hour,2018-01-20T02:00:00
2021-02-28T01:23:45,1,quarter,2021-05-31T01:23:45
""".lstrip()


models__test_dateadd_sql = """
with data as (

    select * from {{ ref('data_dateadd') }}

)

select
    case
        when datepart = 'hour' then {{ dateadd('hour', 'interval_length', 'start_date') }}
        when datepart = 'day' then  {{ dateadd('day', 'interval_length', 'start_date') }}
        when datepart = 'month' then {{ dateadd('month', 'interval_length', 'start_date') }}
        when datepart = 'year' then  {{ dateadd('year', 'interval_length', 'start_date') }}
        when datepart = 'quarter' then  {{ dateadd('quarter', 'interval_length', 'start_date') }}
        else null
    end as actual,
    expected
from data
"""


class TestDateAdd(BaseDateAdd):

    @pytest.fixture(scope="class")
    def seeds(self):
        return {"data_dateadd.csv": seeds__data_dateadd_csv}

    @pytest.fixture(scope="class")
    def models(self):
        return {
            "test_dateadd.yml": models__test_dateadd_yml,
            "test_dateadd.sql": self.interpolate_macro_namespace(
                models__test_dateadd_sql, "dateadd"
            ),
        }


class TestDateTrunc(BaseDateTrunc):

    @pytest.fixture(scope="class")
    def seeds(self):
        return {"data_date_trunc.csv": seeds__data_date_trunc_csv}


class TestLastDay(BaseLastDay):
    pass
