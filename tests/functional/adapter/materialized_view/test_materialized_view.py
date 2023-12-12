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
from dbt.tests.adapter.materialized_view.changes import (
    MaterializedViewChanges,
    MaterializedViewChangesApplyMixin,
    MaterializedViewChangesContinueMixin,
    MaterializedViewChangesFailMixin,
)
from dbt.tests.adapter.materialized_view.files import MY_TABLE, MY_VIEW, MY_SEED

from dbt.tests.util import (
    assert_message_in_logs,
    get_model_file,
    run_dbt,
    run_dbt_and_capture,
    set_model_file,
)
from tests.functional.adapter.materialized_view.utils import (
    query_relation_type,
    query_rewrite_enabled,
    query_build_mode,
    query_refresh_mode,
    query_refresh_method
)

MY_MATERIALIZED_VIEW = """
{{ config(
    materialized='materialized_view',
    refresh_mode='demand',
    refresh_method='force',
    build_mode='immediate'
) }}
select * from {{ ref('my_seed') }}
"""


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


class OracleMaterializedViewChanges(MaterializedViewChanges):

    """
    refresh_mode: Refresh mode of the materialized view
        DEMAND - Oracle Database refreshes this materialized view whenever an appropriate refresh procedure is called
        COMMIT - Oracle Database refreshes this materialized view when a transaction on one of the materialized view's masters commits
        NEVER - Oracle Database never refreshes this materialized view

    refresh_method: Default method used to refresh the materialized view (can be overridden through the API)
        COMPLETE (C) - Materialized view is completely refreshed from the masters
        FORCE (?) - Oracle Database performs a fast refresh if possible, otherwise a complete refresh
        FAST (F) - Oracle Database performs an incremental refresh applying changes that correspond to changes in the masters since the last refresh
        NEVER (N) - User specified that the Oracle Database should not refresh this materialized view

    build_mode: Indicates how the materialized view was populated during creation
        IMMEDIATE - Populated from the masters during creation
        DEFERRED - Not populated during creation. Must be explicitly populated later by the user.
        PREBUILT - Populated with an existing table during creation. The relationship of the contents of this prebuilt table to the materialized view's masters is unknown to the Oracle Database.

    rewrite_enabled: Indicates whether rewrite is enabled (Y) or not (N)

    """

    @pytest.fixture(scope="function", autouse=True)
    def setup(self, project, my_materialized_view):
        # make sure the model in the data reflects the files each time
        run_dbt(["seed"])
        run_dbt(["run", "--models", my_materialized_view.identifier, "--full-refresh"])

        # the tests touch these files, store their contents in memory
        initial_model = get_model_file(project, my_materialized_view)

        yield

        # and then reset them after the test runs
        set_model_file(project, my_materialized_view, initial_model)

    @pytest.fixture(scope="class", autouse=True)
    def models(self):
        yield {
            "my_table.sql": MY_TABLE,
            "my_view.sql": MY_VIEW,
            "my_materialized_view.sql": MY_MATERIALIZED_VIEW,
        }

    @staticmethod
    def query_relation_type(project, relation: BaseRelation) -> Optional[str]:
        return query_relation_type(project, relation)

    @staticmethod
    def check_start_state(project, materialized_view):
        """
          refresh_mode: Optional[str] = "demand"
          refresh_method: Optional[str] = "force"
          build_mode: Optional[str] = "immediate"
          query_rewrite: Optional[str] = "disable"
        """
        assert query_rewrite_enabled(project, materialized_view) == "disable"
        assert query_build_mode(project, materialized_view) == "IMMEDIATE"
        assert query_refresh_mode(project, materialized_view) == "DEMAND"
        assert query_refresh_method(project, materialized_view) == "FORCE"

    @staticmethod
    def change_config_via_alter(project, materialized_view):
        initial_model = get_model_file(project, materialized_view)
        new_model = initial_model.replace("build_mode='immediate'", "build_mode='DEFERRED'")
        set_model_file(project, materialized_view, new_model)

    @staticmethod
    def change_config_via_replace(project, materialized_view):
        initial_model = get_model_file(project, materialized_view)
        new_model = initial_model.replace("refresh_method='force'", "refresh_method='COMPLETE'")
        set_model_file(project, materialized_view, new_model)

    @staticmethod
    def check_state_alter_change_is_applied(project, materialized_view):
        assert query_build_mode(project, materialized_view) == 'DEFERRED'

    @staticmethod
    def check_state_replace_change_is_applied(project, materialized_view):
        assert query_refresh_method(project, materialized_view) == 'COMPLETE'


class TestOracleMaterializedViewChangesApply(
    OracleMaterializedViewChanges, MaterializedViewChangesApplyMixin
):
    def test_change_is_applied_via_alter(self, project, my_materialized_view):
        self.check_start_state(project, my_materialized_view)

        self.change_config_via_alter(project, my_materialized_view)

        _, logs = run_dbt_and_capture(["--debug", "run", "--models", my_materialized_view.name], expect_pass=True)

        self.check_state_alter_change_is_applied(project, my_materialized_view)

        assert_message_in_logs(f"Applying ALTER to: {my_materialized_view}", logs)
        assert_message_in_logs(f"Applying REPLACE to: {my_materialized_view}", logs, False)

    def test_change_is_applied_via_replace(self, project, my_materialized_view):
        self.check_start_state(project, my_materialized_view)

        self.change_config_via_alter(project, my_materialized_view)
        self.change_config_via_replace(project, my_materialized_view)
        _, logs = run_dbt_and_capture(["--debug", "run", "--models", my_materialized_view.name])

        self.check_state_alter_change_is_applied(project, my_materialized_view)
        self.check_state_replace_change_is_applied(project, my_materialized_view)
        view_name = f"{my_materialized_view}".upper()
        assert_message_in_logs(f"Applying REPLACE to: {view_name}", logs)

    def test_full_refresh_occurs_with_changes(self, project, my_materialized_view):
        self.change_config_via_alter(project, my_materialized_view)
        self.change_config_via_replace(project, my_materialized_view)
        _, logs = run_dbt_and_capture(
            ["--debug", "run", "--models", my_materialized_view.identifier, "--full-refresh"]
        )
        assert self.query_relation_type(project, my_materialized_view) == "materialized_view"
        assert_message_in_logs(f"Applying ALTER to: {my_materialized_view}", logs, False)
        view_name = f"{my_materialized_view}".upper()
        assert_message_in_logs(f"Applying REPLACE to: {view_name}", logs)
