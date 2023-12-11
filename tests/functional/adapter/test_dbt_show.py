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
from dbt.tests.util import run_dbt

from dbt.tests.adapter.dbt_show.fixtures import models__second_ephemeral_model
from dbt.tests.adapter.dbt_show.test_dbt_show import BaseShowSqlHeader, BaseShowLimit

models__sql_header = """
{% call set_sql_header(config) %}
with variables as (
    select 1 as my_variable from dual
)
{%- endcall %}
select my_variable from variables
"""


class TestOracleShowLimit(BaseShowLimit):

    @pytest.mark.parametrize(
        "args,expected",
        [
            ([], 5),  # default limit
            (["--limit", 3], 3),  # fetch 3 rows
            (["--limit", -1], 7),  # fetch all rows
        ],
    )
    def test_limit(self, project, args, expected):
        run_dbt(["build"])
        dbt_args = ["show", "--inline", models__second_ephemeral_model, *args]
        results = run_dbt(dbt_args)
        assert len(results.results[0].agate_table) == expected
        # ensure limit was injected in compiled_code when limit specified in command args
        limit = results.args.get("limit")
        if limit > 0:
            assert f"fetch first { limit } rows only" in results.results[0].node.compiled_code


class TestOracleShowSqlHeader(BaseShowSqlHeader):

    @pytest.fixture(scope="class")
    def models(self):
        return {
            "sql_header.sql": models__sql_header,
        }
