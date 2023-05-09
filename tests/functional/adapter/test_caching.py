"""
Copyright (c) 2023, Oracle and/or its affiliates.
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

from dbt.tests.adapter.caching.test_caching import (
    BaseCachingLowercaseModel,
    BaseCachingUppercaseModel,
    BaseCachingSelectedSchemaOnly,
)

model_sql = """
{{
    config(
        materialized='table'
    )
}}
select 1 as id from dual
"""

another_schema_model_sql = """
{{
    config(
        materialized='table',
        schema='another_schema'
    )
}}
select 1 as id from dual
"""


class TestCachingLowerCaseModel(BaseCachingLowercaseModel):

    @pytest.fixture(scope="class")
    def models(self):
        return {
            "model.sql": model_sql,
        }


class TestCachingUppercaseModel(BaseCachingUppercaseModel):

    @pytest.fixture(scope="class")
    def models(self):
        return {
            "MODEL.sql": model_sql,
        }


class TestCachingSelectedSchemaOnly(BaseCachingSelectedSchemaOnly):

    @pytest.fixture(scope="class")
    def models(self):
        return {
            "model.sql": model_sql,
            "another_schema_model.sql": another_schema_model_sql,
        }
