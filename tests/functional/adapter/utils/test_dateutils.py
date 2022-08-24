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
from dbt.tests.adapter.utils.test_datediff import BaseDateDiff

from dbt.tests.adapter.utils.fixture_dateadd import models__test_dateadd_yml
from dbt.tests.adapter.utils.fixture_datediff import models__test_datediff_yml

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


seeds__data_datediff_csv = """first_date,second_date,datepart,result
2018-01-01 01:00:00,2018-01-02 01:00:00,day,1
2018-01-01 01:00:00,2018-02-01 01:00:00,month,1
2018-01-01 01:00:00,2019-01-01 01:00:00,year,1
2018-01-01 01:00:00,2018-01-01 02:00:00,hour,1
2018-01-01 01:00:00,2018-01-01 02:01:00,minute,61
2018-01-01 01:00:00,2018-01-01 02:00:01,second,3601
2019-12-31 00:00:00,2019-12-27 00:00:00,week,-1
2019-12-31 00:00:00,2019-12-30 00:00:00,week,0
2019-12-31 00:00:00,2020-01-02 00:00:00,week,0
2019-12-31 00:00:00,2020-01-06 02:00:00,week,1
,2018-01-01 02:00:00,hour,
2018-01-01 02:00:00,,hour,
"""


models__test_datediff_sql = """
with data as (

    select * from {{ ref('data_datediff') }}

)

select

    case
        when datepart = 'second' then {{ datediff('first_date', 'second_date', 'second') }}
        when datepart = 'minute' then {{ datediff('first_date', 'second_date', 'minute') }}
        when datepart = 'hour' then {{ datediff('first_date', 'second_date', 'hour') }}
        when datepart = 'day' then {{ datediff('first_date', 'second_date', 'day') }}
        when datepart = 'week' then {{ datediff('first_date', 'second_date', 'week') }}
        when datepart = 'month' then {{ datediff('first_date', 'second_date', 'month') }}
        when datepart = 'year' then {{ datediff('first_date', 'second_date', 'year') }}
        else null
    end as actual,
    result as expected

from data
-- Also test correct casting of literal values.
union all 
    select {{ datediff("TO_TIMESTAMP('1999-12-31 23:59:59.999999', 'YYYY-MM-DD HH24:MI:SS.FF')",
                       "TO_TIMESTAMP('2000-01-01 00:00:00.000000', 'YYYY-MM-DD HH24:MI:SS.FF')", 
                       "minute") }} as actual, 
                       1 as expected FROM DUAL

union all 
    select {{ datediff("TO_TIMESTAMP('1999-12-31 23:59:59.999999', 'YYYY-MM-DD HH24:MI:SS.FF')",
                       "TO_TIMESTAMP('2000-01-01 00:00:00.000000', 'YYYY-MM-DD HH24:MI:SS.FF')",
                        "hour") }} as actual, 
                        1 as expected FROM DUAL
                        
union all 
    select {{ datediff("TO_TIMESTAMP('1999-12-31 23:59:59.999999', 'YYYY-MM-DD HH24:MI:SS.FF')",
                       "TO_TIMESTAMP('2000-01-01 00:00:00.000000', 'YYYY-MM-DD HH24:MI:SS.FF')",
                       "day") }} as actual, 
                       1 as expected FROM DUAL
                       
union all 
    select {{ datediff("TO_TIMESTAMP('1999-12-31 23:59:59.999999', 'YYYY-MM-DD HH24:MI:SS.FF')",
                       "TO_TIMESTAMP('2000-01-03 00:00:00.000000', 'YYYY-MM-DD HH24:MI:SS.FF')",
                       "week") }} as actual, 
                       1 as expected FROM DUAL
union all 
    select {{ datediff("TO_TIMESTAMP('1999-12-31 23:59:59.999999', 'YYYY-MM-DD HH24:MI:SS.FF')",
                       "TO_TIMESTAMP('2000-01-01 00:00:00.000000', 'YYYY-MM-DD HH24:MI:SS.FF')",
                       "month") }} as actual, 
                       1 as expected FROM DUAL
union all 
    select {{ datediff("TO_TIMESTAMP('1999-12-31 23:59:59.999999', 'YYYY-MM-DD HH24:MI:SS.FF')",
                       "TO_TIMESTAMP('2000-01-01 00:00:00.000000', 'YYYY-MM-DD HH24:MI:SS.FF')",
                       "quarter") }} as actual, 
                       1 as expected FROM DUAL
union all 
    select {{ datediff("TO_TIMESTAMP('1999-12-31 23:59:59.999999', 'YYYY-MM-DD HH24:MI:SS.FF')",
                       "TO_TIMESTAMP('2000-01-01 00:00:00.000000', 'YYYY-MM-DD HH24:MI:SS.FF')",
                       "year") }} as actual, 
                       1 as expected FROM DUAL
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


class TestDateDiff(BaseDateDiff):

    @pytest.fixture(scope="class")
    def seeds(self):
        return {"data_datediff.csv": seeds__data_datediff_csv}

    @pytest.fixture(scope="class")
    def models(self):
        return {
            "test_datediff.yml": models__test_datediff_yml,
            "test_datediff.sql": self.interpolate_macro_namespace(
                models__test_datediff_sql, "datediff"
            ),
        }
