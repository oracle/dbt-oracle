# Snapshots

`dbt snapshots` provides a mechanism to record changes to a mutable table over time. To demonstrate snapshots we use the `sh.promotions` table.

In dbt, snapshots are select statements, defined within a snapshot block in a .sql file, typically within a `snapshots` directory.

## On the first run
dbt will create the initial snapshot table — this will be the result set of the select statement, with additional columns including `dbt_valid_from` and `dbt_valid_to`. All records will have a `dbt_valid_to = null`.


## Subsequent runs - Detect row changes

dbt will detect changes in a row based on the configured strategy. There are 2 built-in strategies
`timestamp` and `check`

- **timestamp** - Uses an `updated_at` field to determine if a row is changed. If the configured `updated_at` column for a row is more recent than the last time the snapshot ran, then dbt will invalidate the old record and record the new one.
If the timestamps are unchanged, then dbt will not take any action


- **check** - The check strategy is useful for tables which do not have a reliable updated_at column. This strategy works by comparing a list of columns between their current and historical values. If any of these columns have changed, then dbt will invalidate the old record and record the new one. If the column values are identical, then dbt will not take any action.

## Example

### Snapshot SQL

We would like to record changes in the table `promotion_costs`. Below is the snapshot SQL which refers the `promotion_costs` table

```sql
--snapshots/promotion_costs.sql
{% snapshot promotion_costs_snapshot %}
    {{        config(
                strategy='check',
                unique_key='promo_id',
                check_cols='all',
            )
    }}
    select * from {{ ref('promotion_costs') }}
{% endsnapshot %}

```

### On first run

```sql
CREATE  TABLE dbt_test.promotion_costs_snapshot

  AS


    SELECT sbq.*,
        ora_hash(coalesce(CAST(promo_id AS VARCHAR(50) ), '')
         || '|' || coalesce(CAST(to_timestamp('2022-01-03 16:56:03.052125','yyyy/mm/dd hh24:mi:ss.ff') AS VARCHAR(50) ), '')
        ) AS dbt_scd_id,
        to_timestamp('2022-01-03 16:56:03.052125','yyyy/mm/dd hh24:mi:ss.ff') AS dbt_updated_at,
        to_timestamp('2022-01-03 16:56:03.052125','yyyy/mm/dd hh24:mi:ss.ff') AS dbt_valid_from,
        CAST(nullif(to_timestamp('2022-01-03 16:56:03.052125','yyyy/mm/dd hh24:mi:ss.ff'), to_timestamp('2022-01-03 16:56:03.052125','yyyy/mm/dd hh24:mi:ss.ff')) AS DATE) AS dbt_valid_to
    FROM (


    SELECT * FROM dbt_test.promotion_costs
    ) sbq

```

An example of one row in the snapshot data with promo_id = 37

| PROMO_ID |	PROMO_NAME	| PROMO_COST |	DBT_UPDATED_AT |	DBT_VALID_FROM | DBT_VALID_TO	| DBT_SCD_ID |
|-----|---|---|---|---|----|----|
| 37 |	blowout sale |	0 |	2022-01-03 16:56:03.052125000 | 2022-01-03  16:56:03.052125000 | (null)	|	3740524032 |


### Subsequent runs

Assume that the promotion cost for promo id = 37 is changed to 20 from 0. If we now run the dbt snapshot command, the change will be recorded in the following way.

| PROMO_ID |	PROMO_NAME	| PROMO_COST |	DBT_UPDATED_AT |	DBT_VALID_FROM | DBT_VALID_TO	| DBT_SCD_ID |
|-----|---|---|---|---|----|----|
| 37 |	blowout sale |	0 |	2022-01-03 16:56:03.052125000 | 2022-01-03 16:56:03.052125000 | 2022-01-03 17:20:58	|	3740524032 |
| 37 | blowout sale | 20 | 2022-01-03 17:20:58.483295000 | 2022-01-03 17:20:58.483295000 | (null) | 494897153 |

#### SQL queries

```sql
CREATE GLOBAL TEMPORARY TABLE o$pt_promotion_costs_snapshot142033
  ON COMMIT PRESERVE ROWS
  AS
    WITH snapshot_query AS (
        SELECT * FROM dbt_test.promotion_costs
    ),

    snapshotted_data AS (
        SELECT dbt_test.promotion_costs_snapshot.*,
            promo_id AS dbt_unique_key
        FROM dbt_test.promotion_costs_snapshot
        WHERE dbt_valid_to IS NULL
    ),

    insertions_source_data AS (

        SELECT
            snapshot_query.*,
            promo_id AS dbt_unique_key,
            to_timestamp('2022-01-06 14:20:32.465942','yyyy/mm/dd hh24:mi:ss.ff') AS dbt_updated_at,
            to_timestamp('2022-01-06 14:20:32.465942','yyyy/mm/dd hh24:mi:ss.ff') AS dbt_valid_from,
            nullif(to_timestamp('2022-01-06 14:20:32.465942','yyyy/mm/dd hh24:mi:ss.ff'), to_timestamp('2022-01-06 14:20:32.465942','yyyy/mm/dd hh24:mi:ss.ff')) AS dbt_valid_to,
            ora_hash(coalesce(CAST(promo_id AS VARCHAR(50) ), '')
         || '|' || coalesce(CAST(to_timestamp('2022-01-06 14:20:32.465942','yyyy/mm/dd hh24:mi:ss.ff') AS VARCHAR(50) ), '')
        ) AS dbt_scd_id

        FROM snapshot_query
    ),

    updates_source_data AS (

        SELECT
            snapshot_query.*,
            promo_id AS dbt_unique_key,
            to_timestamp('2022-01-06 14:20:32.465942','yyyy/mm/dd hh24:mi:ss.ff') AS dbt_updated_at,
            to_timestamp('2022-01-06 14:20:32.465942','yyyy/mm/dd hh24:mi:ss.ff') AS dbt_valid_from,
            to_timestamp('2022-01-06 14:20:32.465942','yyyy/mm/dd hh24:mi:ss.ff') AS dbt_valid_to

        FROM snapshot_query
    ),

    insertions AS (

        SELECT
            'insert' AS dbt_change_type,
            source_data.*

        FROM insertions_source_data source_data
        LEFT OUTER JOIN snapshotted_data ON snapshotted_data.dbt_unique_key = source_data.dbt_unique_key
        WHERE snapshotted_data.dbt_unique_key IS NULL
           OR (
                snapshotted_data.dbt_unique_key IS NOT NULL
            AND (
                (snapshotted_data.promo_id != source_data.promo_id
        OR
        (
            ((snapshotted_data.promo_id IS NULL) AND NOT (source_data.promo_id IS NULL))
            OR
            ((NOT snapshotted_data.promo_id IS NULL) AND (source_data.promo_id IS NULL))
        ) OR snapshotted_data.promo_name != source_data.promo_name
        OR
        (
            ((snapshotted_data.promo_name IS NULL) AND NOT (source_data.promo_name IS NULL))
            OR
            ((NOT snapshotted_data.promo_name IS NULL) AND (source_data.promo_name IS NULL))
        ) OR snapshotted_data.promo_subcategory != source_data.promo_subcategory
        OR
        (
            ((snapshotted_data.promo_subcategory IS NULL) AND NOT (source_data.promo_subcategory IS NULL))
            OR
            ((NOT snapshotted_data.promo_subcategory IS NULL) AND (source_data.promo_subcategory IS NULL))
        ) OR snapshotted_data.promo_subcategory_id != source_data.promo_subcategory_id
        OR
        (
            ((snapshotted_data.promo_subcategory_id IS NULL) AND NOT (source_data.promo_subcategory_id IS NULL))
            OR
            ((NOT snapshotted_data.promo_subcategory_id IS NULL) AND (source_data.promo_subcategory_id IS NULL))
        ) OR snapshotted_data.promo_category != source_data.promo_category
        OR
        (
            ((snapshotted_data.promo_category IS NULL) AND NOT (source_data.promo_category IS NULL))
            OR
            ((NOT snapshotted_data.promo_category IS NULL) AND (source_data.promo_category IS NULL))
        ) OR snapshotted_data.promo_category_id != source_data.promo_category_id
        OR
        (
            ((snapshotted_data.promo_category_id IS NULL) AND NOT (source_data.promo_category_id IS NULL))
            OR
            ((NOT snapshotted_data.promo_category_id IS NULL) AND (source_data.promo_category_id IS NULL))
        ) OR snapshotted_data.promo_cost != source_data.promo_cost
        OR
        (
            ((snapshotted_data.promo_cost IS NULL) AND NOT (source_data.promo_cost IS NULL))
            OR
            ((NOT snapshotted_data.promo_cost IS NULL) AND (source_data.promo_cost IS NULL))
        ) OR snapshotted_data.promo_begin_date != source_data.promo_begin_date
        OR
        (
            ((snapshotted_data.promo_begin_date IS NULL) AND NOT (source_data.promo_begin_date IS NULL))
            OR
            ((NOT snapshotted_data.promo_begin_date IS NULL) AND (source_data.promo_begin_date IS NULL))
        ) OR snapshotted_data.promo_end_date != source_data.promo_end_date
        OR
        (
            ((snapshotted_data.promo_end_date IS NULL) AND NOT (source_data.promo_end_date IS NULL))
            OR
            ((NOT snapshotted_data.promo_end_date IS NULL) AND (source_data.promo_end_date IS NULL))
        ) OR snapshotted_data.promo_total != source_data.promo_total
        OR
        (
            ((snapshotted_data.promo_total IS NULL) AND NOT (source_data.promo_total IS NULL))
            OR
            ((NOT snapshotted_data.promo_total IS NULL) AND (source_data.promo_total IS NULL))
        ) OR snapshotted_data.promo_total_id != source_data.promo_total_id
        OR
        (
            ((snapshotted_data.promo_total_id IS NULL) AND NOT (source_data.promo_total_id IS NULL))
            OR
            ((NOT snapshotted_data.promo_total_id IS NULL) AND (source_data.promo_total_id IS NULL))
        ))
            )
        )

    ),

    updates AS (

        SELECT
            'update' AS dbt_change_type,
            source_data.*,
            snapshotted_data.dbt_scd_id

        FROM updates_source_data source_data
        JOIN snapshotted_data ON snapshotted_data.dbt_unique_key = source_data.dbt_unique_key
        WHERE (
            (snapshotted_data.promo_id != source_data.promo_id
        OR
        (
            ((snapshotted_data.promo_id IS NULL) AND NOT (source_data.promo_id IS NULL))
            OR
            ((NOT snapshotted_data.promo_id IS NULL) AND (source_data.promo_id IS NULL))
        ) OR snapshotted_data.promo_name != source_data.promo_name
        OR
        (
            ((snapshotted_data.promo_name IS NULL) AND NOT (source_data.promo_name IS NULL))
            OR
            ((NOT snapshotted_data.promo_name IS NULL) AND (source_data.promo_name IS NULL))
        ) OR snapshotted_data.promo_subcategory != source_data.promo_subcategory
        OR
        (
            ((snapshotted_data.promo_subcategory IS NULL) AND NOT (source_data.promo_subcategory IS NULL))
            OR
            ((NOT snapshotted_data.promo_subcategory IS NULL) AND (source_data.promo_subcategory IS NULL))
        ) OR snapshotted_data.promo_subcategory_id != source_data.promo_subcategory_id
        OR
        (
            ((snapshotted_data.promo_subcategory_id IS NULL) AND NOT (source_data.promo_subcategory_id IS NULL))
            OR
            ((NOT snapshotted_data.promo_subcategory_id IS NULL) AND (source_data.promo_subcategory_id IS NULL))
        ) OR snapshotted_data.promo_category != source_data.promo_category
        OR
        (
            ((snapshotted_data.promo_category IS NULL) AND NOT (source_data.promo_category IS NULL))
            OR
            ((NOT snapshotted_data.promo_category IS NULL) AND (source_data.promo_category IS NULL))
        ) OR snapshotted_data.promo_category_id != source_data.promo_category_id
        OR
        (
            ((snapshotted_data.promo_category_id IS NULL) AND NOT (source_data.promo_category_id IS NULL))
            OR
            ((NOT snapshotted_data.promo_category_id IS NULL) AND (source_data.promo_category_id IS NULL))
        ) OR snapshotted_data.promo_cost != source_data.promo_cost
        OR
        (
            ((snapshotted_data.promo_cost IS NULL) AND NOT (source_data.promo_cost IS NULL))
            OR
            ((NOT snapshotted_data.promo_cost IS NULL) AND (source_data.promo_cost IS NULL))
        ) OR snapshotted_data.promo_begin_date != source_data.promo_begin_date
        OR
        (
            ((snapshotted_data.promo_begin_date IS NULL) AND NOT (source_data.promo_begin_date IS NULL))
            OR
            ((NOT snapshotted_data.promo_begin_date IS NULL) AND (source_data.promo_begin_date IS NULL))
        ) OR snapshotted_data.promo_end_date != source_data.promo_end_date
        OR
        (
            ((snapshotted_data.promo_end_date IS NULL) AND NOT (source_data.promo_end_date IS NULL))
            OR
            ((NOT snapshotted_data.promo_end_date IS NULL) AND (source_data.promo_end_date IS NULL))
        ) OR snapshotted_data.promo_total != source_data.promo_total
        OR
        (
            ((snapshotted_data.promo_total IS NULL) AND NOT (source_data.promo_total IS NULL))
            OR
            ((NOT snapshotted_data.promo_total IS NULL) AND (source_data.promo_total IS NULL))
        ) OR snapshotted_data.promo_total_id != source_data.promo_total_id
        OR
        (
            ((snapshotted_data.promo_total_id IS NULL) AND NOT (source_data.promo_total_id IS NULL))
            OR
            ((NOT snapshotted_data.promo_total_id IS NULL) AND (source_data.promo_total_id IS NULL))
        ))
        )
    )

    SELECT * FROM insertions
    UNION ALL
    SELECT * FROM updates
```

```sql
MERGE INTO dbt_test.promotion_costs_snapshot d
    USING dbt_test.o$pt_promotion_costs_snapshot142033 s
    ON (s.dbt_scd_id = d.dbt_scd_id)

    WHEN MATCHED
        THEN UPDATE
        SET dbt_valid_to = s.dbt_valid_to
        WHERE d.dbt_valid_to IS NULL
          AND s.dbt_change_type IN ('update', 'delete')
    WHEN NOT MATCHED
        THEN INSERT (d.promo_id, d.promo_name, d.promo_subcategory, d.promo_subcategory_id, d.promo_category, d.promo_category_id, d.promo_cost, d.promo_begin_date, d.promo_end_date, d.promo_total, d.promo_total_id, d.dbt_updated_at, d.dbt_valid_from, d.dbt_valid_to, d.dbt_scd_id)
        VALUES (s.promo_id, s.promo_name, s.promo_subcategory, s.promo_subcategory_id, s.promo_category, s.promo_category_id, s.promo_cost, s.promo_begin_date, s.promo_end_date, s.promo_total, s.promo_total_id, s.dbt_updated_at, s.dbt_valid_from, s.dbt_valid_to, s.dbt_scd_id)
        WHERE s.dbt_change_type = 'insert'

```



