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

from dbt.tests.adapter.grants.test_model_grants import BaseModelGrants, model_schema_yml
from dbt.tests.adapter.grants.test_incremental_grants import BaseIncrementalGrants, incremental_model_schema_yml
from dbt.tests.adapter.grants.test_invalid_grants import BaseInvalidGrants
from dbt.tests.adapter.grants.test_seed_grants import BaseSeedGrants
from dbt.tests.adapter.grants.test_snapshot_grants import BaseSnapshotGrants, snapshot_schema_yml

my_model_sql = """
  select 1 as fun from dual
"""

my_incremental_model_sql = """
  select 1 as fun from dual
"""

my_invalid_model_sql = """
  select 1 as fun from dual
"""

my_snapshot_sql = """
{% snapshot my_snapshot %}
    {{ config(
        check_cols='all', unique_key='id', strategy='check',
        target_database=database, target_schema=schema
    ) }}
    select 1 as id, cast('blue' as {{ type_string() }}) as color from dual
{% endsnapshot %}
""".strip()


class TestSeedGrantsOracle(BaseSeedGrants):
    pass


class TestModelGrantsOracle(BaseModelGrants):

    @pytest.fixture(scope="class")
    def models(self):
        updated_schema = self.interpolate_name_overrides(model_schema_yml)

        return {
            "my_model.sql": my_model_sql,
            "schema.yml": updated_schema,
        }


class TestIncrementalGrantsOracle(BaseIncrementalGrants):

    @pytest.fixture(scope="class")
    def models(self):
        updated_schema = self.interpolate_name_overrides(incremental_model_schema_yml)
        return {
            "my_incremental_model.sql": my_incremental_model_sql,
            "schema.yml": updated_schema,
        }


class TestInvalidGrantsOracle(BaseInvalidGrants):

    def grantee_does_not_exist_error(self):
        return "ORA-01917: user or role"

    def privilege_does_not_exist_error(self):
        return "ORA-00990: missing or invalid privilege"

    @pytest.fixture(scope="class")
    def models(self):
        return {
            "my_invalid_model.sql": my_invalid_model_sql,
        }


class TestSnapshotGrantsOracle(BaseSnapshotGrants):

    @pytest.fixture(scope="class")
    def snapshots(self):
        return {
            "my_snapshot.sql": my_snapshot_sql,
            "schema.yml": self.interpolate_name_overrides(snapshot_schema_yml),
        }
