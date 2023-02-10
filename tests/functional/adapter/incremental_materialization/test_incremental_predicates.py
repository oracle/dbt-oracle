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
from dbt.tests.adapter.incremental.test_incremental_predicates import BaseIncrementalPredicates


models__delete_insert_incremental_predicates_sql = """
{{ config(
    materialized = 'incremental',
    unique_key = 'id'
) }}

{% if not is_incremental() %}

select 1 as id, 'hello' as msg, 'blue' as color from dual
union all
select 2 as id, 'goodbye' as msg, 'red' as color from dual

{% else %}

-- delete will not happen on the above record where id = 2, so new record will be inserted instead
select 1 as id, 'hey' as msg, 'blue' as color from dual
union all
select 2 as id, 'yo' as msg, 'green' as color from dual
union all
select 3 as id, 'anyway' as msg, 'purple' as color from dual

{% endif %}
"""

class TestIncrementalPredicatesMergeOracle(BaseIncrementalPredicates):

    @pytest.fixture(scope="class")
    def models(self):
        return {
            "delete_insert_incremental_predicates.sql": models__delete_insert_incremental_predicates_sql
        }

    @pytest.fixture(scope="class")
    def project_config_update(self):
        return {
            "models": {
                "+incremental_predicates": [
                    "dbt_internal_dest.id != 2"
                ],
                "+incremental_strategy": "merge"
            }
        }


class TestPredicatesMergeOracle(BaseIncrementalPredicates):

    @pytest.fixture(scope="class")
    def models(self):
        return {
            "delete_insert_incremental_predicates.sql": models__delete_insert_incremental_predicates_sql
        }

    @pytest.fixture(scope="class")
    def project_config_update(self):
        return {
            "models": {
                "+predicates": [
                    "dbt_internal_dest.id != 2"
                ],
                "+incremental_strategy": "merge"
            }
        }
