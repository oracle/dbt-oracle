# Integration testing with Oracle's Autonomous Database Service (ADBS)

## Always Free Autonomous Database

To test the integration with ADBS, you can use OCI's [Always Free Autonomous Database](https://docs.oracle.com/en-us/iaas/Content/Database/Concepts/adbfreeoverview.htm). The database is provided free of charge.
- Processor: 1 Oracle CPU processor (cannot be scaled)
- Database Storage: 20 GB storage (cannot be scaled)
- Workload Type could be either ATP (Autonomous Transaction Processing) or ADW (Autonomous Data Warehouse)

The database also provides a read-only Sales History data set. Any user can start querying the tables in this Sales History `sh` schema. Models in this test project refer the `sh` schema. You do not need to load any other dataset.

## Setup the oracle profile

To setup [profiles.yml](profiles.yml) read [setup & installation instructions][1] on dbt docs website

Install dbt-oracle in your project's virtual environment.


## dbt project

Next, run the `dbt compile` command in this project directory to compile the models and resolve dependencies.
```bash
dbt compile --profiles-dir ./
```
```text
20:14:29  Running with dbt=1.0.1
20:14:29  Found 10 models, 5 tests, 1 snapshot, 1 analysis, 382 macros, 2 operations, 1 seed file, 8 sources, 2 exposures, 0 metrics
20:14:29  
20:14:32  Concurrency: 4 threads (target='dev')
20:14:32  
20:14:33  Done.
```
All dbt models in this test project refer the sales history (`sh`) sample schema.
Following directory structure shows the 10 models, seed, test, analysis and snaphots.


```text
.
├── README.md
├── analysis
│   └── eu_customers.sql
├── data
│   └── seed.csv
├── dbt_packages
│   └── dbt_utils
├── dbt_project.yml
├── macros
│   ├── demo_multiple_statements.sql
│   ├── execute_statements.sql
│   └── readme.md
├── models
│   ├── direct_sales_channel_promo_cost.sql
│   ├── eu
│       ├── countries.sql
│       └── eu_direct_sales_channels_promo_costs.sql
│   ├── income_levels.sql
│   ├── internet_sales_channel_customers.sql
│   ├── people.sql
│   ├── promotion_costs.sql
│   ├── sales_internet_channel.sql
│   ├── schema.yml
│   ├── us_product_sales_channel_ranking.sql
│   └── us_seed_customers.sql
├── packages.yml
├── profiles.yml
├── seeds
│   └── seed.csv
├── snapshots
│   ├── README.md
│   └── promotion_costs.sql
└── test
    └── test_count_employees.sql


```

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
