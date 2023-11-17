"""
Copyright (c) 2022, Oracle and/or its affiliates.

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
from typing import Optional, Tuple

import pytest

from dbt.adapters.base.relation import BaseRelation

from dbt.tests.adapter.materialized_view.basic import MaterializedViewBasic
from dbt.tests.util import (
    assert_message_in_logs,
    get_model_file,
    run_dbt,
    run_dbt_and_capture,
    set_model_file,
)
from tests.functional.adapter.materialized_view.utils import query_relation_type


class TestOracleMaterializedViewBasic(MaterializedViewBasic):

    @staticmethod
    def insert_record(project, table: BaseRelation, record: Tuple[int, int]):
        my_id, value = record
        project.run_sql(f"insert into {table} (id, value) values ({my_id}, {value})")

    @staticmethod
    def refresh_materialized_view(project, materialized_view: BaseRelation):
        sql = f"""
            BEGIN
             DBMS_MVIEW.REFRESH('{materialized_view}');
            END;
        """
        project.run_sql(sql)

    @staticmethod
    def query_row_count(project, relation: BaseRelation) -> int:
        sql = f"select count(*) from {relation}"
        return project.run_sql(sql, fetch="one")[0]

    @staticmethod
    def query_relation_type(project, relation: BaseRelation) -> Optional[str]:
        return query_relation_type(project, relation)

    @pytest.fixture(scope="function", autouse=True)
    def setup(self, project, my_materialized_view):

        run_dbt(["seed"])
        run_dbt(["run", "--models", my_materialized_view.identifier, "--full-refresh"])

        # the tests touch these files, store their contents in memory
        initial_model = get_model_file(project, my_materialized_view)

        yield

        # and then reset them after the test runs
        set_model_file(project, my_materialized_view, initial_model)
        run_dbt(["run-operation", "drop_schema", "--args", f"relation: {my_materialized_view.schema}"])

    @pytest.mark.skip(
        "The current implementation does not support overwriting materialized views with tables."
    )
    def test_table_replaces_materialized_view(self, project, my_materialized_view):
        super().test_table_replaces_materialized_view(project, my_materialized_view)

    @pytest.mark.skip(
        "The current implementation does not support overwriting materialized views with views."
    )
    def test_view_replaces_materialized_view(self, project, my_materialized_view):
        super().test_view_replaces_materialized_view(project, my_materialized_view)

    def test_materialized_view_full_refresh(self, project, my_materialized_view):
        _, logs = run_dbt_and_capture(
            ["--debug", "run", "--models", my_materialized_view.identifier, "--full-refresh"]
        )
        assert self.query_relation_type(project, my_materialized_view) == "materialized_view"
        view_name = f"{my_materialized_view}".upper()
        assert_message_in_logs(f"Applying REPLACE to: {view_name}", logs)

