# Integration testing with Oracle's Autonomous Database Service (ADBS)

## Always Free Autonomous Database

To test the integration with ADBS, you can use OCI's [Always Free Autonomous Database](https://docs.oracle.com/en-us/iaas/Content/Database/Concepts/adbfreeoverview.htm). The database is provided free of charge.
- Processor: 1 Oracle CPU processor (cannot be scaled)
- Database Storage: 20 GB storage (cannot be scaled)
- Workload Type could be either ATP (Autonomous Transaction Processing) or ADW (Autonomous Data Warehouse)

The database also provides a read-only Sales History data set. Any user can start querying the tables in this Sales History `sh` schema. Models in this test project refer the `sh` schema. You do not need to load any other dataset.

## Setup

[Install][1] dbt-oracle and setup [profiles.yml](profiles.yml) for ADBS

### Verify the installation

```bash
dbt --version
```

```text
Core:
  - installed: 1.3.0
  - latest:    1.3.0 - Up to date!
```

### Check database connectivity

```bash
dbt debug --profiles-dir ./
```

```text
dbt version: 1.3.0
python version: 3.8.13
..
..
Connection:
  user: 
  database:
  schema:
  ...
  Connection test: [OK connection ok]

All checks passed!

```
After this, you can test various dbt features included in this project

## Features tested in this project

| Feature | Command | Corresponding File |
| --------|---------|----- |
| Connection | `dbt debug` | [profiles.yml](profiles.yml)
| Data Sources | `dbt run` or `dbt test` | [schema.yml](./models/schema.yml)
| Seeds | `dbt seed` | [seed.csv](./data/seed.csv)
| View Materialization | `dbt run` | [direct_sales_channel_promo_cost.sql](./models/direct_sales_channel_promo_cost.sql)
| Table Materialization | `dbt run` | [sales_internet_channel.sql](./models/sales_internet_channel.sql)
| Ephemeral Materialization | `dbt run` | [income_levels.sql](./models/income_levels.sql) & [us_seed_customers.sql](./models/us_seed_customers.sql)
| Incremental Materialization | `dbt run` | [us_product_sales_channel_ranking.sql](./models/us_product_sales_channel_ranking.sql)
| Singular Test | `dbt test` | [test_count_employees.sql](./test/test_count_employees.sql)
| Generic Test - Not null | `dbt test` | [schema.yml](./models/schema.yml)
| Generic Test - Unique values | `dbt test` | [schema.yml](./models/schema.yml)
| Generic Test - Accepted values | `dbt test` | [schema.yml](./models/schema.yml)
| Generic Test - Relationships | `dbt test` | [schema.yml](./models/schema.yml)
| Operations |  `dbt run-operation`  | Check [macros](macros)
| Snapshots | `dbt snapshot` | Check [snapshots](snapshots)
| Analyses | `dbt compile` | [eu_customers.sql](./analysis/eu_customers.sql)
| Exposures | `dbt run` or `dbt test` | [exposures.yml](./models/exposures.yml)
| Generate documentation | `dbt docs generate` |
| Serve project documentation on port 8080 | `dbt docs serve`


## Tests [TODO]
- Metrics - Experimental feature introduced in dbt-core==1.0.0

[1]: https://docs.getdbt.com/reference/warehouse-profiles/oracle-profile
