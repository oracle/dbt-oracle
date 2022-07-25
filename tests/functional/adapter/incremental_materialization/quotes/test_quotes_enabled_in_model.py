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

import datetime
from pathlib import Path

import pytest
from dbt.tests.util import run_dbt

# seeds/my_seed.csv
seed_csv = """
user_id,user_name,birth_date,income,last_login_date,description
1,Easton,1981-05-20,40000,2022-04-25T08:57:59,login
2,Lillian,1978-09-03,54000,2022-04-25T08:58:59,login
3,Jeremiah,1982-03-11,10000,2022-04-25T09:57:59,login
4,Nolan,1976-05-06,900000,2022-04-25T09:58:59,login
""".lstrip()

model_yml = """
version: 2
models:
  - name: my_incr_model
    columns:
     - name: user_name
       quote: true
     - name: user_id
       quote: true
     - name: birth_date
       quote: true
     - name: income
       quote: true
     - name: last_login_date
       quote: true
     - name: description
       quote: true
"""


# models/my_incr_model.sql
my_incr_model_sql = """
{{config(materialized='incremental', 
         merge_update_columns=["user_name", "birth_date", "income", "last_login_date", "description"],
         unique_key='user_id')}}
SELECT * FROM {{ ref('seed') }}
{% if is_incremental() %}
    WHERE "last_login_date" > (SELECT max("last_login_date") FROM {{ this }})
{% endif %}

"""

# seeds/add_new_rows.sql
seeds__add_new_rows_sql = """
-- insert two new rows, both of which should be in incremental model
INSERT ALL
    INTO {schema}.seed ("user_id", "user_name", "birth_date", "income", "last_login_date", "description") VALUES 
        (2,'Lillian Sr.', TO_DATE('1982-02-03', 'YYYY-MM-DD'), 200000, TO_DATE('2022-05-01 06:01:31', 'YYYY-MM-DD HH:MI:SS'), 'Login')
    INTO {schema}.seed ("user_id", "user_name", "birth_date", "income", "last_login_date", "description") VALUES 
        (5,'John Doe',TO_DATE('1992-10-01', 'YYYY-MM-DD'), 300000, TO_DATE('2022-06-01 06:01:31', 'YYYY-MM-DD HH:MI:SS'), 'Login')
SELECT * FROM dual
"""


class TestIncrementalMergeQuotedColumnsConfigYml:

    @pytest.fixture(scope="class")
    def seeds(self):
        return {
            "seed.csv": seed_csv,
            "add_new_rows.sql": seeds__add_new_rows_sql
        }

    @pytest.fixture(scope="class")
    def models(self):
        return {
            "my_incr_model.sql": my_incr_model_sql,
            "schema.yml": model_yml
        }

    @pytest.fixture(scope="class")
    def project_config_update(self):
        return {
            "seeds": {
                "quote_columns": True
            },
        }

    def test_run_dbt(self, project):
        """
            - run seed
            - run incremental model
            - add new rows
            - run incremental model

        The following SQL is expected to run.

        """
        results = run_dbt(['seed'])
        assert len(results) == 1

        results = run_dbt(['run'])
        assert len(results) == 1

        project.run_sql_file(Path("seeds") / Path("add_new_rows.sql"))

        results = run_dbt(['run'])
        assert len(results) == 1

        user_id_2_query = 'SELECT * FROM {}.{} WHERE "user_id" = {}'.format(project.test_schema,
                                                                            'my_incr_model',
                                                                             2)
        expected_result = [(2, 'Lillian Sr.',
                            datetime.datetime(1982, 2, 3, 0, 0),
                            200000,
                            datetime.datetime(2022, 5, 1, 6, 1, 31),
                            'Login')]

        result = project.run_sql(user_id_2_query, fetch="all")
        assert result == expected_result

        used_id_5_query = 'SELECT * FROM {}.{} WHERE "user_id" = {}'.format(project.test_schema,
                                                                            'my_incr_model',
                                                                             5)
        expected_result = [(5,  'John Doe',
                            datetime.datetime(1992, 10, 1, 0, 0),
                            300000,
                            datetime.datetime(2022, 6, 1, 6, 1, 31),
                            'Login')]

        result = project.run_sql(used_id_5_query, fetch="all")
        assert result == expected_result


