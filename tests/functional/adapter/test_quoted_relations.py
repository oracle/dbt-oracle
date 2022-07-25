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

import datetime

from dbt.tests.util import run_dbt, relation_from_name


# seeds/my_seed.csv
seed_csv = """
user_id,user_name,birth_date,income,last_login_date
1,Easton,1981-05-20,40000,2022-04-25T08:57:59
2,Lillian,1978-09-03,54000,2022-04-25T08:58:59
3,Jeremiah,1982-03-11,10000,2022-04-25T09:57:59
4,Nolan,1976-05-06,900000,2022-04-25T09:58:59
""".lstrip()

# models/foo.sql
my_model_foo_sql = """
{{config(materialized='table', 
         alias="foo")}}
SELECT * FROM {{ ref('seed') }}
"""

# models/foo2.sql
my_model_foo2_sql = """
{{config(materialized='table', 
         alias="Foo")}}
SELECT * FROM {{ ref('seed') }}
"""


class TestQuotedLowerCaseTableName:

    @pytest.fixture(scope="class")
    def seeds(self):
        return {
            "seed.csv": seed_csv,
        }

    @pytest.fixture(scope="class")
    def models(self):
        return {
            "my_model_foo.sql": my_model_foo_sql,
        }

    @pytest.fixture(scope="class")
    def project_config_update(self):
        return {
            "quoting": {
                "database": False,
                "schema": False,
                "identifier": True
            },
        }

    def test_run_dbt(self, project):
        """
            - run seed
            - run model

        """
        results = run_dbt(['seed'])
        assert len(results) == 1

        results = run_dbt(['run'])
        assert len(results) == 1

        results = run_dbt(['run'])
        assert len(results) == 1

        sql = 'SELECT COUNT(*) from "foo"'
        result = project.run_sql(sql, fetch="all")
        assert result == [(4,)]


class TestQuotedTitleCaseTableName:

    @pytest.fixture(scope="class")
    def seeds(self):
        return {
            "seed.csv": seed_csv,
        }

    @pytest.fixture(scope="class")
    def models(self):
        return {
            "my_model_foo.sql": my_model_foo2_sql,
        }

    @pytest.fixture(scope="class")
    def project_config_update(self):
        return {
            "quoting": {
                "database": False,
                "schema": False,
                "identifier": True
            },
        }

    def test_run_dbt(self, project):
        """
            - run seed
            - run model

        """
        results = run_dbt(['seed'])
        assert len(results) == 1

        results = run_dbt(['run'])
        assert len(results) == 1

        results = run_dbt(['run'])
        assert len(results) == 1

        sql = 'SELECT COUNT(*) from "Foo"'
        result = project.run_sql(sql, fetch="all")
        assert result == [(4,)]


class TestUnQuotedLowerCaseTableName:

    @pytest.fixture(scope="class")
    def seeds(self):
        return {
            "seed.csv": seed_csv,
        }

    @pytest.fixture(scope="class")
    def models(self):
        return {
            "my_model_foo.sql": my_model_foo_sql,
        }

    def test_run_dbt(self, project):
        """
            - run seed
            - run model

        """
        results = run_dbt(['seed'])
        assert len(results) == 1

        results = run_dbt(['run'])
        assert len(results) == 1

        results = run_dbt(['run'])
        assert len(results) == 1

        sql = 'SELECT COUNT(*) from FOO'
        result = project.run_sql(sql, fetch="all")
        assert result == [(4,)]


class TestUnQuotedTitleCaseTableName:

    @pytest.fixture(scope="class")
    def seeds(self):
        return {
            "seed.csv": seed_csv,
        }

    @pytest.fixture(scope="class")
    def models(self):
        return {
            "my_model_foo.sql": my_model_foo2_sql,
        }

    def test_run_dbt(self, project):
        """
            - run seed
            - run model

        """
        results = run_dbt(['seed'])
        assert len(results) == 1

        results = run_dbt(['run'])
        assert len(results) == 1

        results = run_dbt(['run'])
        assert len(results) == 1

        sql = 'SELECT COUNT(*) from FOO'
        result = project.run_sql(sql, fetch="all")
        assert result == [(4,)]


