"""
Copyright (c) 2023, Oracle and/or its affiliates.

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

from tests.functional.adapter.constraints.fixtures import (model_schema_yml,
                                                           constrained_model_schema_yml,
                                                           my_model_sql,
                                                           my_model_with_nulls_sql,
                                                           my_model_wrong_name_sql,
                                                           my_model_wrong_order_sql,
                                                           my_model_view_wrong_name_sql,
                                                           my_model_view_wrong_order_sql,
                                                           my_model_incremental_wrong_name_sql,
                                                           my_model_incremental_wrong_order_sql,
                                                           my_model_incremental_with_nulls_sql,
                                                           my_incremental_model_sql)

from dbt.tests.adapter.constraints.test_constraints import (
    BaseTableConstraintsColumnsEqual,
    BaseViewConstraintsColumnsEqual,
    BaseIncrementalConstraintsColumnsEqual,
    BaseConstraintsRuntimeDdlEnforcement,
    BaseIncrementalConstraintsRuntimeDdlEnforcement,
    BaseConstraintsRollback,
    BaseIncrementalConstraintsRollback,
    BaseModelConstraintsRuntimeEnforcement
)

_expected_sql_oracle = """
create table <model_identifier> (
    id not null primary key check (id > 0),
    color,
    date_day
) as select
        id,
        color,
        date_day from
    (
    select
        'blue' as color,
        1 as id,
        TO_DATE('2019-01-01', 'YYYY-MM-DD') as date_day
        from dual
    ) model_subq
"""


class OracleColumnsEqualSetup:

    @pytest.fixture
    def string_type(self):
        return "CHAR"

    @pytest.fixture
    def int_type(self):
        return "NUMBER"

    @pytest.fixture
    def data_types(self, schema_int_type, int_type, string_type):
        # sql_column_value, schema_data_type, error_data_type
        return [
            ["1", schema_int_type, int_type],
            ["'1'", string_type, string_type],
            ["TO_DATE('2019-01-01', 'YYYY-MM-DD')", 'date', "DATE"]]


class TestOracleTableConstraintsColumnsEqual(OracleColumnsEqualSetup, BaseTableConstraintsColumnsEqual):

    @pytest.fixture(scope="class")
    def models(self):
        return {
            "my_model_wrong_order.sql": my_model_wrong_order_sql,
            "my_model_wrong_name.sql": my_model_wrong_name_sql,
            "constraints_schema.yml": model_schema_yml,
        }


class TestOracleViewConstraintsColumnsEqual(OracleColumnsEqualSetup, BaseViewConstraintsColumnsEqual):

    @pytest.fixture(scope="class")
    def models(self):
        return {
            "my_model_wrong_order.sql": my_model_view_wrong_order_sql,
            "my_model_wrong_name.sql": my_model_view_wrong_name_sql,
            "constraints_schema.yml": model_schema_yml,
        }


class TestOracleIncrementalConstraintsColumnsEqual(OracleColumnsEqualSetup, BaseIncrementalConstraintsColumnsEqual):

    @pytest.fixture(scope="class")
    def models(self):
        return {
            "my_model_wrong_order.sql": my_model_incremental_wrong_order_sql,
            "my_model_wrong_name.sql": my_model_incremental_wrong_name_sql,
            "constraints_schema.yml": model_schema_yml,
        }


class TestOracleTableConstraintsDdlEnforcement(BaseConstraintsRuntimeDdlEnforcement):

    @pytest.fixture(scope="class")
    def models(self):
        return {
            "my_model.sql": my_model_wrong_order_sql,
            "constraints_schema.yml": model_schema_yml,
        }

    @pytest.fixture(scope="class")
    def expected_sql(self):
        return _expected_sql_oracle


class TestOracleIncrementalConstraintsDdlEnforcement(BaseIncrementalConstraintsRuntimeDdlEnforcement):

    @pytest.fixture(scope="class")
    def models(self):
        return {
            "my_model.sql": my_model_incremental_wrong_order_sql,
            "constraints_schema.yml": model_schema_yml,
        }

    @pytest.fixture(scope="class")
    def expected_sql(self):
        return _expected_sql_oracle


class TestOracleTableConstraintsRollback(BaseConstraintsRollback):

    @pytest.fixture(scope="class")
    def models(self):
        return {
            "my_model.sql": my_model_sql,
            "constraints_schema.yml": model_schema_yml,
        }

    @pytest.fixture(scope="class")
    def null_model_sql(self):
        return my_model_with_nulls_sql

    @pytest.fixture(scope="class")
    def expected_error_messages(self):
        return ["ORA-01400: cannot insert NULL into"]


class TestOracleIncrementalConstraintsRollback(BaseIncrementalConstraintsRollback):

    @pytest.fixture(scope="class")
    def models(self):
        return {
            "my_model.sql": my_incremental_model_sql,
            "constraints_schema.yml": model_schema_yml,
        }

    @pytest.fixture(scope="class")
    def null_model_sql(self):
        return my_model_incremental_with_nulls_sql

    @pytest.fixture(scope="class")
    def expected_error_messages(self):
        return ["ORA-01400: cannot insert NULL into"]


class TestOracleModelConstraintsRuntimeEnforcement(BaseModelConstraintsRuntimeEnforcement):

    @pytest.fixture(scope="class")
    def models(self):
        return {
            "my_model.sql": my_model_sql,
            "constraints_schema.yml": constrained_model_schema_yml,
        }

    @pytest.fixture(scope="class")
    def expected_sql(self):
        return """
create table <model_identifier> (
    id not null,
    color,
    date_day,
    check (id > 0),
    primary key (id),
    constraint strange_uniqueness_requirement unique (color, date_day)
) as select
        id,
        color,
        date_day from
    (
    select
        1 as id,
        'blue' as color,
        TO_DATE('2019-01-01', 'YYYY-MM-DD') as date_day
        from dual
    ) model_subq
"""
