# Testing

# Table of contents

- [Environment Variables](#environment-variables)
- [Adapter Plugin Tests](#adapter-plugin-tests)
- [Jaffle Shop Test Project](#jaffle-shop-test-project)
- [Testing for different Python versions](#different-python-versions)

## Environment variables <a name='environment-variables'></a>

The following environment variables should be set to test `dbt-oracle`

```bash
    # cx_oracle needs lib_dir parameter pointing to the folder
    # containing the libraries from an unzipped Instant Client Basic or Basic Light package.
    # If lib_dir is not passed client libraries are looked for in the Operating system search path
    # or set in the following environment variables.
    DYLD_LIBRARY_PATH # For MacOS
    LD_LIBRARY_PATH # For Linux

    # For ADB, cx_oracle will need the path to the folder
    # containing client wallet, sqlnet.ora and tnsnames.ora
    TNS_ADMIN

    # Database connection config - dbt specific variables
    DBT_ORACLE_USER
    DBT_ORACLE_HOST
    DBT_ORACLE_PORT
    DBT_ORACLE_SERVICE
    DBT_ORACLE_PASSWORD
    DBT_ORACLE_DATABASE
    DBT_ORACLE_SCHEMA
```

## Adapter Plugin Tests <a name='adapter-plugin-tests'></a>

dbt-labs has developed a package [dbt-adapter-tests](https://github.com/dbt-labs/dbt-adapter-tests) which defines a test suite for adapter plugins

It can be installed using
```bash
pip install pytest-dbt-adapter
```
The spec file [oracle.dbtspec](oracle.dbtspec) lists all test sequences for Python 3.7+

To run the test cases, type the following command depending on the Python version.
```bash
pytest tests/oracle.dbtspec tests/test_config.py # For Python 3.7, 3.8 and 3.9

# or

pytest tests/oracle_py36.dbtspect tests/test_config.py # For Python 3.6
```

All test cases are passing for Python 3.7, 3.8 and 3.9

```text
tests/oracle.dbtspec::test_dbt_empty
tests/oracle.dbtspec::test_dbt_base
tests/oracle.dbtspec::test_dbt_ephemeral
tests/oracle.dbtspec::test_dbt_incremental
tests/oracle.dbtspec::test_dbt_snapshot_strategy_timestamp
tests/oracle.dbtspec::test_dbt_snapshot_strategy_check_cols
tests/oracle.dbtspec::test_dbt_schema_test
tests/oracle.dbtspec::test_dbt_data_test
tests/oracle.dbtspec::test_dbt_ephemeral_data_tests
```

Known failing test for Python 3.6
```text
FAILED tests/oracle.dbtspec::test_dbt_empty

Unknown error: assert False == True
 +  where True = <function exists at 0x101907dc0>('/var/folders/mj/j31vvz790kj3hg62qr465sj40000gn/T/tmpcfuj_knn/project/target/run_results.json')
 +    where <function exists at 0x101907dc0> = <module 'posixpath' from '/usr/local/Cellar/python@3.8/3.8.12_1/bin/../Frameworks/Python.framework/Versions/3.8/lib/python3.8/posixpath.py'>.exists
 +      where <module 'posixpath' from '/usr/local/Cellar/python@3.8/3.8.12_1/bin/../Frameworks/Python.framework/Versions/3.8/lib/python3.8/posixpath.py'> = os.path in test index 1 (item_type=run_results)
```

### Overriding defaults

#### All test sequences

Reason for override -> **ORA-00904: "ID": invalid identifier**

As shown below, during seed table creation and insertion, column names are quoted. 

```sql
create table dbt_test.newcolumns 
    ("id" number,"name" varchar2(16),"some_date" timestamp,"last_initial" varchar2(16))

insert all
            into dbt_test.newcolumns ("id", "name", "some_date", "last_initial") values(:p1,:p2,:p3,:p4)
            into dbt_test.newcolumns ("id", "name", "some_date", "last_initial") values(:p1,:p2,:p3,:p4)
            into dbt_test.newcolumns ("id", "name", "some_date", "last_initial") values(:p1,:p2,:p3,:p4)
            into dbt_test.newcolumns ("id", "name", "some_date", "last_initial") values(:p1,:p2,:p3,:p4)
```

In subsequent select queries, seed table columns are not quoted and hence the following error

```text
22:29:38.841013 [debug] [Thread-1  ]: Database Error in snapshot cc_all_snapshot (snapshots/cc_all_snapshot.sql)
  ORA-00904: "ID": invalid identifier
  compiled SQL at target/run/dbt_test_project/snapshots/cc_all_snapshot.sql
Traceback (most recent call last):
  File "/Users/abhisoms/dbt-oracle/dbt/adapters/oracle/connections.py", line 205, in exception_handler
    yield
  File "/Users/abhisoms/dbt-oracle/dbt/adapters/oracle/connections.py", line 258, in add_query
    cursor.execute(sql, bindings)
cx_Oracle.DatabaseError: ORA-00904: "ID": invalid identifier

```

We override the seed configuration in `dbt_project.yml` in the following way

```yaml
projects:
  - overrides:  data_test_ephemeral_models
    dbt_project_yml: &override-dbt-project
       seeds:
          dbt_test_project:
             quote_columns: false
```

#### tests/oracle.dbtspec::test_dbt_ephemeral_data_tests

Reason for override -> **ORA-32034: unsupported use of WITH clause**

```sql
-- models/ephemeral.sql
-- https://github.com/dbt-labs/dbt-adapter-tests/blob/main/pytest_dbt_adapter/builtin.py#L308-L313
with my_cool_cte as (
  select name, id from {{ ref('base') }}
)
select id, name from my_cool_cte where id is not null

```
Following is the compiled SQL by dbt. `ORA-32034: unsupported use of WITH clause` is a result of nested WITH clause

```sql
-- models/passing_model.sql
-- ORA-32034: unsupported use of WITH clause
create view dbt_test.passing_model as
    with  dbt__cte__ephemeral__ as (


with my_cool_cte as (
  select name, id from dbt_test.base
)
select id, name from my_cool_cte where id is not null
),my_other_cool_cte as (
    select id, name from dbt__cte__ephemeral__
    where id > 1000
)
select name, id from my_other_cool_cte
```

We can override `models/ephemeral.sql` in the following way

```yaml
# tests/oracle.dbtspec
projects:
  - overrides:  data_test_ephemeral_models
    paths:
      models/ephemeral.sql: |
        {{ config(materialized='ephemeral') }}
        select name, id from {{ ref('base') }} where id is not null
```
final SQL which is run.
```sql
--Correct SQL after override
create view dbt_test.passing_model as

    with dbt__cte__ephemeral__ as (
        select name, id
        from dbt_test.base
        where id is not null),

         my_other_cool_cte as (
            select id, name
            from dbt__cte__ephemeral__
            where id > 1000)

select name, id from my_other_cool_cte


```

## Jaffle Shop Test Project <a name='jaffle-shop-test-project'></a>

[Jaffle Shop test project](https://github.com/dbt-labs/jaffle_shop) is a self-contained dbt project which can be used for testing the adapter.

### Profile

Setup a `jaffle_shop` profile to connect to the Oracle Database

```yaml
# ~/.dbt/profiles.yml
jaffle_shop:
  target: dev
  outputs:
    dev:
      type: oracle
      user: "{{ env_var('DBT_ORACLE_USER') }}"
      pass: "{{ env_var('DBT_ORACLE_PASSWORD') }}"
      protocol: "tcps"
      host: "{{ env_var('DBT_ORACLE_HOST') }}"
      port: 1522
      service: "{{ env_var('DBT_ORACLE_SERVICE') }}"
      database: "{{ env_var('DBT_ORACLE_DATABASE') }}"
      schema: "{{ env_var('DBT_ORACLE_SCHEMA') }}"
      shardingkey:
         - skey
      supershardingkey:
         - sskey
      cclass: CONNECTIVITY_CLASS
      purity: self
      threads: 4

```

### dbt debug

To test connection, run the `dbt debug` command

```text
Connection:
  user: <...>
  database: <...>
  schema: <...>
  protocol: tcps
  host: <...>
  port: 1522
  service: <...>
  connection_string: None
  shardingkey: ['skey']
  supershardingkey: ['sskey']
  cclass: CONNECTIVITY_CLASS
  purity: self
  Connection test: [OK connection ok]

All checks passed!
```


### Seed `quote_columns` config

By default, seed configuration `quote_columns` is expected to be False as explained here https://docs.getdbt.com/reference/resource-configs/quote_columns

However, seed column names are quoted when `dbt seed` command is run.

This raises `ORA-00904: "AMOUNT": invalid identifier` errors in the subsequent `dbt run` command. 

```text
19:12:11.145108 [error] [MainThread]: Database Error in model stg_payments (models/staging/stg_payments.sql)
19:12:11.145796 [error] [MainThread]:   ORA-00904: "AMOUNT": invalid identifier
19:12:11.146445 [error] [MainThread]:   compiled SQL at target/run/jaffle_shop/models/staging/stg_payments.sql
19:12:11.147094 [info ] [MainThread]: 
19:12:11.147972 [error] [MainThread]: Database Error in model stg_orders (models/staging/stg_orders.sql)
19:12:11.148769 [error] [MainThread]:   ORA-00904: "STATUS": invalid identifier
19:12:11.149495 [error] [MainThread]:   compiled SQL at target/run/jaffle_shop/models/staging/stg_orders.sql
19:12:11.150168 [info ] [MainThread]: 
19:12:11.150703 [error] [MainThread]: Database Error in model stg_customers (models/staging/stg_customers.sql)
19:12:11.151226 [error] [MainThread]:   ORA-00904: "LAST_NAME": invalid identifier
19:12:11.151734 [error] [MainThread]:   compiled SQL at target/run/jaffle_shop/models/staging/stg_customers.sql

```

Disable `quote_columns` in `dbt_project.yml`.

```yaml
name: 'jaffle_shop'
version: '0.1'
profile: 'jaffle_shop'
config-version: 2

source-paths: ["models"]
analysis-paths: ["analysis"]
test-paths: ["tests"]
data-paths: ["data"]
macro-paths: ["macros"]

target-path: "target"
clean-targets:
    - "target"
    - "dbt_modules"
    - "logs"

models:
  jaffle_shop:
      materialized: table
      staging:
        materialized: view

# Disable seed config quote_columns
seeds:
    jaffle_shop:
        quote_columns: false
```

### dbt seed

```text

21:20:43  Running with dbt=1.0.1
21:20:44  Found 5 models, 20 tests, 0 snapshots, 0 analyses, 193 macros, 0 operations, 3 seed files, 0 sources, 0 exposures, 0 metrics
21:20:44  
21:20:51  Concurrency: 4 threads (target='dev')
21:20:51  
21:20:51  1 of 3 START seed file dbt_test.raw_customers................................... [RUN]
21:20:51  2 of 3 START seed file dbt_test.raw_orders...................................... [RUN]
21:20:51  3 of 3 START seed file dbt_test.raw_payments.................................... [RUN]
21:20:54  2 of 3 OK loaded seed file dbt_test.raw_orders.................................. [INSERT 99 in 3.56s]
21:20:54  1 of 3 OK loaded seed file dbt_test.raw_customers............................... [INSERT 100 in 3.56s]
21:20:55  3 of 3 OK loaded seed file dbt_test.raw_payments................................ [INSERT 113 in 4.20s]
21:20:57  
21:20:57  Finished running 3 seeds in 13.23s.
21:20:57  
21:20:57  Completed successfully
21:20:57  
21:20:57  Done. PASS=3 WARN=0 ERROR=0 SKIP=0 TOTAL=3

```


### dbt run

```text
21:21:28  Running with dbt=1.0.1
21:21:28  Found 5 models, 20 tests, 0 snapshots, 0 analyses, 193 macros, 0 operations, 3 seed files, 0 sources, 0 exposures, 0 metrics
21:21:28  
21:21:35  Concurrency: 4 threads (target='dev')
21:21:35  
21:21:35  1 of 5 START view model dbt_test.stg_customers.................................. [RUN]
21:21:35  2 of 5 START view model dbt_test.stg_orders..................................... [RUN]
21:21:35  3 of 5 START view model dbt_test.stg_payments................................... [RUN]
21:21:38  2 of 5 OK created view model dbt_test.stg_orders................................ [OK in 3.07s]
21:21:38  3 of 5 OK created view model dbt_test.stg_payments.............................. [OK in 3.07s]
21:21:38  1 of 5 OK created view model dbt_test.stg_customers............................. [OK in 3.07s]
21:21:38  4 of 5 START table model dbt_test.orders........................................ [RUN]
21:21:38  5 of 5 START table model dbt_test.customers..................................... [RUN]
21:21:41  4 of 5 OK created table model dbt_test.orders................................... [OK in 3.63s]
21:21:41  5 of 5 OK created table model dbt_test.customers................................ [OK in 3.61s]
21:21:43  
21:21:43  Finished running 3 view models, 2 table models in 15.27s.
21:21:43  
21:21:43  Completed successfully
21:21:43  
21:21:43  Done. PASS=5 WARN=0 ERROR=0 SKIP=0 TOTAL=5

```

### dbt test

```text
21:23:10  Running with dbt=1.0.1
21:23:10  Found 5 models, 20 tests, 0 snapshots, 0 analyses, 193 macros, 0 operations, 3 seed files, 0 sources, 0 exposures, 0 metrics
21:23:10  
21:23:16  Concurrency: 4 threads (target='dev')
21:23:16  
....
....
....
....
21:23:34  17 of 20 PASS unique_orders_order_id............................................ [PASS in 2.78s]
21:23:35  20 of 20 PASS unique_stg_payments_payment_id.................................... [PASS in 2.08s]
21:23:35  19 of 20 PASS unique_stg_orders_order_id........................................ [PASS in 2.40s]
21:23:37  
21:23:37  Finished running 20 tests in 27.14s.
21:23:37  
21:23:37  Completed successfully
21:23:37  
21:23:37  Done. PASS=20 WARN=0 ERROR=0 SKIP=0 TOTAL=20

```

## Testing for different Python versions <a name='different-python-versions'></a>

### Python 3.7, 3.8 and 3.9

- dbt-core==1.0.1
- pytest-dbt-adapter==0.6.0
- All test cases PASS
  - tests/oracle.dbtspec::test_dbt_empty
  - tests/oracle.dbtspec::test_dbt_base
  - tests/oracle.dbtspec::test_dbt_ephemeral
  - tests/oracle.dbtspec::test_dbt_incremental
  - tests/oracle.dbtspec::test_dbt_snapshot_strategy_timestamp
  - tests/oracle.dbtspec::test_dbt_snapshot_strategy_check_cols
  - tests/oracle.dbtspec::test_dbt_schema_test
  - tests/oracle.dbtspec::test_dbt_data_test
  - tests/oracle.dbtspec::test_dbt_ephemeral_data_tests

### Python 3.6

- dbt-core==0.21.1
- pytest-dbt-adapter==0.4.0
- 1 test case failing.
  - tests/oracle.dbtspec::test_dbt_empty - **FAILING**
  - tests/oracle.dbtspec::test_dbt_base
  - tests/oracle.dbtspec::test_dbt_ephemeral
  - tests/oracle.dbtspec::test_dbt_incremental
  - tests/oracle.dbtspec::test_dbt_snapshot_strategy_timestamp
  - tests/oracle.dbtspec::test_dbt_snapshot_strategy_check_cols
  - tests/oracle.dbtspec::test_dbt_schema_test
  - tests/oracle.dbtspec::test_dbt_data_test
  - tests/oracle.dbtspec::test_dbt_ephemeral_data_tests


`tox` is a command line tool to check if the package installs correctly for different python versions. It also runs all the tests in each of the environments. Check the configuration file [tox.ini](../tox.ini) for details.

To run tox, from command line type
```bash
tox
```
If all tests succeed for all python environments, you will see the below output.

```text
  py36: commands succeeded
  py37: commands succeeded
  py38: commands succeeded
  py39: commands succeeded
  congratulations :)
```
For each environment, you can also see the test runtime as summary
```text
  py36 - 12 passed, 8 warnings in 693.73s (0:11:33)
  py37 - 13 passed, 9 warnings in 673.23s (0:11:13)
  py38 - 13 passed, 9 warnings in 745.82s (0:12:25)
  py39 - 13 passed, 9 warnings in 693.90s (0:11:33)
```
