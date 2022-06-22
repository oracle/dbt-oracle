# Testing

# Table of contents

- [Environment Variables](#environment-variables)
- [Adapter Plugin Tests](#adapter-plugin-tests)
- [Testing for different Python versions](#different-python-versions)
- [Jaffle Shop Test Project](#jaffle-shop-test-project)


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
    DBT_ORACLE_PROTOCOL
    DBT_ORACLE_SERVICE
    DBT_ORACLE_PASSWORD
    DBT_ORACLE_DATABASE
    DBT_ORACLE_SCHEMA
```

## Adapter Plugin Tests <a name='adapter-plugin-tests'></a>

dbt-labs has developed a package [dbt-tests-adapter](https://pypi.org/project/dbt-tests-adapter/) which defines a test suite for adapter plugins

### Setup

Clone the project repository into a local directory.

```bash
git clone git@github.com:oracle/dbt-oracle.git
```

Create a python3.7+ virtual environment
```bash
cd dbt-oracle
python3.8 -m venv .venv
source .venv/bin/activate
```
Install `dbt-oracle` project in development mode
```bash
pip install -e .
```

Install `dbt-tests-adapter` and `pytest` in your project's virtual environment

```bash
pip install dbt-tests-adapter pytest
```

To run the test suite, just type the `pytest` command from the cloned `dbt-oracle` project directory

```pytest
pytest
```

```bash
Run pytest
============================= test session starts ==============================
platform linux -- Python 3.9.13, pytest-7.1.2, pluggy-1.0.0
rootdir: /home/runner/work/dbt-oracle/dbt-oracle, configfile: pytest.ini, testpaths: tests/functional
collected 24 items
tests/functional/adapter/test_basic.py ..........                        [ 41%]
tests/functional/adapter/test_config.py ....                             [ 58%]
tests/functional/adapter/test_incremental_unique_id.py ..........        [100%]
============================= 24 passed in 55.85s ==============================
```

## Testing for different Python versions <a name='different-python-versions'></a>

### Python 3.7, 3.8, 3.9 and 3.10

`tox` is a command line tool to check if the package installs correctly for different python versions. It also runs all the tests in each of the environments. Check the configuration file [tox.ini](../tox.ini) for details.

To run tox, from command line type
```bash
tox
```
If all tests succeed for all python environments, you will see the below output.

```text
  py37: commands succeeded
  py38: commands succeeded
  py39: commands succeeded
  py310: commands succeeded
  congratulations :)

```
For each environment, you can also see the test runtime as summary
```text
  py37 - 24 passed in 771.74s (0:12:51)
  py38 - 24 passed in 746.42s (0:12:26)
  py39 - 24 passed in 755.18s (0:12:35)
  py310 - 24 passed in 764.96s (0:12:44)
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
      threads: 4

```

### dbt debug

To test connection, run the `dbt debug` command from the `jaffle_shop` project directory

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