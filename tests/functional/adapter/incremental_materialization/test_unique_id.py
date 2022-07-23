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
from dbt.tests.adapter.incremental.test_incremental_unique_id import (BaseIncrementalUniqueKey,
                                                                      seeds__seed_csv,
                                                                      models__empty_str_unique_key_sql,
                                                                      models__expected__one_str__overwrite_sql,
                                                                      models__empty_unique_key_list_sql,
                                                                      models__no_unique_key_sql,
                                                                      models__not_found_unique_key_sql,
                                                                      models__str_unique_key_sql,
                                                                      models__trinary_unique_key_list_sql,
                                                                      models__unary_unique_key_list_sql,
                                                                      models__nontyped_trinary_unique_key_list_sql,
                                                                      models__duplicated_unary_unique_key_list_sql,
                                                                      models__not_found_unique_key_list_sql,
                                                                      models__expected__unique_key_list__inplace_overwrite_sql)

seeds__add_new_rows_sql = """
-- Insert statement which when applied to seed.csv sees incremental model
--   grow in size while not (necessarily) diverging from the seed itself.

-- insert two new rows, both of which should be in incremental model
--   with any unique columns
INSERT ALL
    INTO {schema}.seed (state, county, city, last_visit_date) VALUES ('WA','King','Seattle',TO_DATE('2022-02-01', 'YYYY-MM-DD'))
    INTO {schema}.seed (state, county, city, last_visit_date) VALUES ('CA','Los Angeles','Los Angeles',TO_DATE('2022-02-01', 'YYYY-MM-DD'))
SELECT * FROM dual
"""

seeds__duplicate_insert_sql = """
-- Insert statement which when applied to seed.csv triggers the inplace
--   overwrite strategy of incremental models. Seed and incremental model
--   diverge.

-- insert new row, which should not be in incremental model
--  with primary or first three columns unique
insert into {schema}.seed
    (state, county, city, last_visit_date)
values ('CT','Hartford','Hartford', TO_DATE('2022-02-14', 'YYYY-MM-DD'));

"""

models__expected__unique_key_list__inplace_overwrite_sql = """
SELECT
    'CT' AS state,
    'Hartford' AS county,
    'Hartford' AS city,
    TO_DATE('2022-02-14', 'YYYY-MM-DD') as last_visit_date FROM DUAL
union all
SELECT 'MA','Suffolk','Boston',TO_DATE('2020-02-12',  'YYYY-MM-DD') FROM DUAL
union all
SELECT 'NJ','Mercer','Trenton',TO_DATE('2022-01-01',  'YYYY-MM-DD') FROM DUAL
union all
SELECT 'NY','Kings','Brooklyn', TO_DATE('2021-04-02',  'YYYY-MM-DD') FROM DUAL
union all
SELECT 'NY','New York','Manhattan', TO_DATE('2021-04-01',  'YYYY-MM-DD') FROM DUAL
union all
SELECT 'PA','Philadelphia','Philadelphia', TO_DATE('2021-05-21', 'YYYY-MM-DD') FROM DUAL
"""

models__expected__one_str__overwrite_sql  = """
SELECT
    'CT' AS state,
    'Hartford' AS county,
    'Hartford' AS city,
    TO_DATE('2022-02-14', 'YYYY-MM-DD') as last_visit_date FROM DUAL
union all
SELECT 'MA','Suffolk','Boston',TO_DATE('2020-02-12',  'YYYY-MM-DD') FROM DUAL
union all
SELECT 'NJ','Mercer','Trenton',TO_DATE('2022-01-01',  'YYYY-MM-DD') FROM DUAL
union all
SELECT 'NY','Kings','Brooklyn', TO_DATE('2021-04-02',  'YYYY-MM-DD') FROM DUAL
union all
SELECT 'NY','New York','Manhattan', TO_DATE('2021-04-01',  'YYYY-MM-DD') FROM DUAL
union all
SELECT 'PA','Philadelphia','Philadelphia', TO_DATE('2021-05-21', 'YYYY-MM-DD') FROM DUAL
"""


class TestIncrementalUniqueKey(BaseIncrementalUniqueKey):

    @pytest.fixture(scope="class")
    def models(self):
        return {
            "trinary_unique_key_list.sql": models__trinary_unique_key_list_sql,
            "nontyped_trinary_unique_key_list.sql": models__nontyped_trinary_unique_key_list_sql,
            "unary_unique_key_list.sql": models__unary_unique_key_list_sql,
            "not_found_unique_key.sql": models__not_found_unique_key_sql,
            "empty_unique_key_list.sql": models__empty_unique_key_list_sql,
            "no_unique_key.sql": models__no_unique_key_sql,
            "empty_str_unique_key.sql": models__empty_str_unique_key_sql,
            "str_unique_key.sql": models__str_unique_key_sql,
            "duplicated_unary_unique_key_list.sql": models__duplicated_unary_unique_key_list_sql,
            "not_found_unique_key_list.sql": models__not_found_unique_key_list_sql,
            "expected": {
                "one_str__overwrite.sql": models__expected__one_str__overwrite_sql,
                "unique_key_list__inplace_overwrite.sql": models__expected__unique_key_list__inplace_overwrite_sql,
            },
        }

    @pytest.fixture(scope="class")
    def seeds(self):
        return {
            "duplicate_insert.sql": seeds__duplicate_insert_sql,
            "seed.csv": seeds__seed_csv,
            "add_new_rows.sql": seeds__add_new_rows_sql,
        }
