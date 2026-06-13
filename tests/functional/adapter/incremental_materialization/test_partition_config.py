"""
Copyright (c) 2026, Oracle and/or its affiliates.

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

from dbt.tests.util import run_dbt


incremental_model_sql = """
{{
    config(
        materialized='incremental',
        unique_key='id',
        incremental_strategy='merge'
    )
}}

select 1 as id, 'initial' as value from dual

{% if is_incremental() %}
union all
select 2 as id, 'incremental' as value from dual
{% endif %}
"""


partitioned_schema_yml = """
version: 2

models:
  - name: incremental_model
    config:
      partition_config:
        clause: "partition by hash (id) partitions 4"
        apply_to_existing: true
"""


class TestIncrementalPartitionConfig:
    @pytest.fixture(scope="class")
    def schema(self):
        return "test_incremental_partition_config"

    @pytest.fixture(scope="class")
    def models(self):
        return {
            "incremental_model.sql": incremental_model_sql,
        }

    def test_incremental_applies_partition_config_to_existing_table(self, project):
        results = run_dbt(["run"])
        assert len(results) == 1
        assert self._is_partitioned(project, "incremental_model") == "NO"

        models_dir = project.project_root / "models"
        (models_dir / "schema.yml").write_text(partitioned_schema_yml, encoding="utf-8")

        results = run_dbt(["run"])
        assert len(results) == 1
        assert self._is_partitioned(project, "incremental_model") == "YES"

    @staticmethod
    def _is_partitioned(project, identifier):
        return project.run_sql(
            f"""
            select partitioned
            from user_tables
            where table_name = upper('{identifier}')
            """,
            fetch="one",
        )[0]
