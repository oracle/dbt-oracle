{#
 Copyright (c) 2024, Oracle and/or its affiliates.

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

     https://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
#}

{#
 Legacy hash function ORA_HASH is known to have collisions in large datasets
 causing errors in snapshot merge statement. Please check the below Github
 issues:

    https://github.com/oracle/dbt-oracle/issues/52
    https://github.com/oracle/dbt-oracle/issues/102

This hash function is used in the marcro oracle__snapshot_hash_arguments

dbt-oracle 1.9 will switch to a stronger hash function - SHA256. Changing the
hash function will invalidate existing snapshots.These helper macros will
ensure a smoother transition to dbt-oracle 1.9.

It is recommended for teams to switch to SHA256 hash function before
dbt-oracle 1.9 using a 2-step process:
1. Create a macro oracle__snapshot_hash_arguments(args) in your dbt project
   Copy paste the contents of macro
   oracle__snapshot_standard_hash_arguments(args) shown below. This will become
   the default from dbt-oracle 1.9

2. Run the following operation on your snapshot table

dbt --debug run-operation update_legacy_dbt_scd_id \
    --args '{snapshot_table: PROMOTION_COSTS_SNAPSHOT, cols: ["promo_id", "dbt_updated_at"]}'

#}

{% macro oracle__snapshot_standard_hash_arguments(args) -%}
    STANDARD_HASH({%- for arg in args -%}
        coalesce(cast({{ arg }} as varchar(4000) ), '')
        {% if not loop.last %} || '|' || {% endif %}
    {%- endfor -%}, 'SHA256')
{%- endmacro %}


{% macro update_legacy_dbt_scd_id(snapshot_table, cols) -%}

   {%- call statement('update_legacy_dbt_scd_id_dtype') -%}
    BEGIN
        UPDATE {{ snapshot_table }} SET DBT_SCD_ID = NULL;
        COMMIT;
        EXECUTE IMMEDIATE 'ALTER TABLE {{ snapshot_table }} MODIFY (dbt_scd_id RAW(32))';
    END;
    {%- endcall -%}

    {%- call statement('update_legacy_dbt_scd_id') -%}
    BEGIN
        UPDATE {{ snapshot_table }}
        SET dbt_scd_id = {{ oracle__snapshot_standard_hash_arguments(cols) }};
        COMMIT;
    END;
    {%- endcall -%}
{%- endmacro %}
