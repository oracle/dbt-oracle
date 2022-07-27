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
from pathlib import Path

from dbt.tests.util import run_dbt

# seeds/my_seed.csv
my_seed_csv = """
id,name,some_date
1,Easton,1981-05-20T06:46:51
2,Lillian,1978-09-03T18:10:33
3,Jeremiah,1982-03-11T03:59:51
4,Nolan,1976-05-06T20:21:35
""".lstrip()


cc_all_snapshot_sql = """
{% snapshot cc_all_snapshot %}
    {{ config(
        check_cols='all', 
        unique_key='id', 
        strategy='check',
        target_database=database, 
        target_schema=schema,
        invalidate_hard_deletes=True
    ) }}
    SELECT * FROM {{ ref('seed') }}
{% endsnapshot %}
""".strip()

# seeds/insert.sql
seeds__insert_sql = """
INSERT ALL
    INTO {schema}.seed (id, name, some_date) VALUES 
        (5, 'John Doe', TO_DATE('1982-02-03', 'YYYY-MM-DD'))
SELECT * FROM dual
"""

# seeds/update.sql
seeds__update_sql = """
UPDATE {schema}.seed 
    SET name = 'Lord Easton'
    WHERE id = 1
"""

# seeds/delete.sql
seeds__delete_sql = """
DELETE FROM {schema}.seed WHERE id = 2
"""


class TestSnapshotCheckInvalidateHardDeletes:

    @pytest.fixture(scope="class")
    def seeds(self):
        return {
            "seed.csv": my_seed_csv,
            "insert.sql": seeds__insert_sql,
            "update.sql": seeds__update_sql,
            "delete.sql": seeds__delete_sql

        }

    @pytest.fixture(scope="class")
    def snapshots(self):
        return {
            "cc_all_snapshot.sql": cc_all_snapshot_sql,
        }

    def test_run_dbt(self, project):
        """dbt seed
           dbt snapshot
           Perform insert/update/delete
           dbt snapshot

        MERGE INTO dbt_test.cc_all_snapshot d
            USING o$pt_cc_all_snapshot182811 s
                ON (s.dbt_scd_id = d.dbt_scd_id)
            WHEN MATCHED
                THEN UPDATE
                SET dbt_valid_to = s.dbt_valid_to
                WHERE d.dbt_valid_to IS NULL
                    AND s.dbt_change_type IN ('update', 'delete')
            WHEN NOT MATCHED
                THEN INSERT (d.id, d.name, d.some_date, d.dbt_updated_at, d.dbt_valid_from, d.dbt_valid_to, d.dbt_scd_id)
                VALUES (s.id, s.name, s.some_date, s.dbt_updated_at, s.dbt_valid_from, s.dbt_valid_to, s.dbt_scd_id)
                WHERE s.dbt_change_type = 'insert'

        """
        results = run_dbt(['seed'])
        assert len(results) == 1

        # snapshot command
        results = run_dbt(["snapshot"])
        for result in results:
            assert result.status == "success"

        project.run_sql_file(Path("seeds") / Path("insert.sql"))
        project.run_sql_file(Path("seeds") / Path("update.sql"))
        project.run_sql_file(Path("seeds") / Path("delete.sql"))

        # run snapshot command
        results = run_dbt(["snapshot"])
        for result in results:
            assert result.status == "success"

        snapshot_of_updated_rows = project.run_sql(f"select * from cc_all_snapshot where id=1", fetch="all")
        assert len(snapshot_of_updated_rows) == 2

        # Deleted record will be invalidated. r['dbt_valid_to'] is set to current timestamp.
        snapshot_of_deleted_rows = project.run_sql(f"select * from cc_all_snapshot where id=2", fetch="all")
        assert len(snapshot_of_deleted_rows) == 1



