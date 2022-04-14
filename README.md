# dbt-oracle version 1.0.0

dbt (data build tool) adapter for the Oracle database.
dbt "adapters" are responsible for adapting dbt's functionality to a given database. Check
https://docs.getdbt.com/docs/contributing/building-a-new-adapter

> Prior to version 1.0.0, dbt-oracle was created and maintained by Techindicium - https://github.com/techindicium/dbt-oracle
Contributors in this repo are credited for laying the groundwork and maintaining the adapter till version 0.4.3.
From version 1.0.0, dbt-oracle is maintained and distributed by Oracle.

# Table of contents

- [What is dbt?](#what-is-dbt)
  - [dbt features](#core-concepts)
  - [An Example](#an-example)
- [Installation](#install)
  - [Support](#support)
  - [Core dependencies](#core-dependencies)
- [Getting Started](#getting-started)
- [Documentation](#documentation-todo)
  - [Features](#features)
- [Changes added in this release (v1.0.0)](#changes-in-this-release)
- [Upcoming Features](#upcoming-features)
- [Contributing](#contributing)
- [Security](#security)
- [License](#license)

## What is dbt? <a name='what-is-dbt'></a>

dbt does the T in ELT (Extract, Load, Transform). To work with dbt you need a copy of your data already loaded in your warehouse.

### dbt features <a name='core-concepts'></a>
- With dbt, you can express all transforms with SQL select
  - Different materialization strategies.
    - view
    - table
    - incremental; selective rebuild for new rows
    - ephemeral; Model 1 interpolated into Model 2 as a Common Table Expression (CTE)
  - No need to write boilerplate code
    - All code to create table or views is generated using macros.
  - Idempotence; rerun models
    - If your source data were to stop updating, successive runs of your transformations would still result in the same tables and views in your warehouse.
    - If your production deployment of your transformations were interrupted, the next run of the transformations would result in the same tables and views as if the deployment had not been interrupted.
    - If you manually triggered transformations between scheduled runs, the scheduled run would result in the same tables and views as if the manual runs had not been triggered.
  - All transformation code is accessible and can be version controlled.
- Dependency resolution
  - Use of ref() function ``select * from {{ ref('MODEL_NAME')}}``
  - dbt automatically resolves dependencies in between models and builds a Directed Acyclic Graph (DAG).
    Each path in the DAG can be independently executed using multiple threads.
  - Interpolates the name of database schema
- Includes a built-in testing framework to ensure model accuracy
  - not null
  - unique
  - contains accepted values
  - relationships
  - custom tests
- Generate documentation for your project and render it as a website.
- Use macros to write reusable SQL

### An example <a name='an-example'></a>

dbt model
```oracle
-- models/customer_view.sql
{{config(materialized='view')}}
with customers_filtered as(
    select * from {{ source('sh_database', 'sales') }}
    where cust_id = 14787
)
select * from customers_filtered
```
dbt compiles the above SQL template to run the below DDL statement.
```oracle
create  table dbt_test.customer_view

  as

with customers_filtered as(
    select * from sh.sales
    where cust_id = 14787
)
select * from customers_filtered
```

For dbt documentation, refer https://docs.getdbt.com/docs/introduction

## Installation <a name='install'></a>

dbt-oracle can be installed via the Python Package Index (PyPI) using pip

`pip install -U dbt-oracle`

### Support <a name='support'></a>

dbt-oracle will provide support for the following

- Python versions 3.6, 3.7, 3.8 and 3.9
- Autonomous Database versions 19c and 21c
- OS
  - Linux
  - MacOS
  - Windows

### Core dependencies <a name='core-dependencies'></a>
dbt-oracle requires the following 3 python packages.

`dbt-core==1.0.4`

  - Open source framework for data transformation
  - Jinja Templating and core SQL compilation logic
  - `dbt-core==1.0.4` is preferred as it supports Python 3.7 and higher
  - For Python 3.6, pip will fallback to `dbt-core==0.21.1`
  - Apache 2.0 License

`cx-Oracle==8.3.0`
 - Python driver for Oracle database
 - Oracle client libraries should be installed on the system. For details check, https://cx-oracle.readthedocs.io/en/latest/user_guide/installation.html
 - BSD License

`dataclasses; python_version < '3.7'`
 - dataclasses package was introduced in the standard Python library from Python 3.7. This is conditional dependency and required only for Python 3.6
 - Apache Software License

These core dependencies are defined as install requirements in `setup.py` and `setup.cfg`. Additionally, `dbt-core` defines a list of **required** dependencies which can be found [here](https://pypistats.org/packages/dbt-core)

## Getting Started <a name='getting-started'></a>

Create a dbt project for oracle database using the `dbt init` command. The init command is interactive and will help you get started with a new project.

`dbt init` will:

* ask you the name of the project
* ask you the database adapter you are using i.e. oracle
* prompt to specify necessary connection details

This example shows initialization of test project `dbt_oracle_test_project`

```text
dbt init

    02:01:53  Running with dbt=1.0.4
    Enter a name for your project (letters, digits, underscore): dbt_oracle_test_project
    The profile dbt_oracle_test_project already exists in /Users/abhisoms/.dbt/profiles.yml. Continue and overwrite it? [y/N]: y
    Which database would you like to use?
    [1] oracle
    (Don't see the one you want? https://docs.getdbt.com/docs/available-adapters)
    Enter a number: 1
    protocol (tcp or tcps) [tcps]:
    host (adb.<oci-region>.oraclecloud.com) [{{ env_var('DBT_ORACLE_HOST') }}]:
    port [1522]:
    user (database username) [{{ env_var('DBT_ORACLE_USER') }}]:
    password (database user password) [{{ env_var('DBT_ORACLE_PASSWORD') }}]:
    service (service name in tnsnames.ora) [{{ env_var('DBT_ORACLE_SERVICE') }}]:
    dbname (database name in which dbt objects should be created) [{{ env_var('DBT_ORACLE_DATABASE') }}]:
    schema (database schema in which dbt objects should be created) [{{ env_var('DBT_ORACLE_SCHEMA') }}]:
    threads (1 or more) [1]: 4

```

Then it will:

Create a new folder with project name and sample files to get you started
  ```text
   ├── README.md
   ├── analyses
   ├── dbt_project.yml
   ├── macros
   ├── models
   │   └── example
   ├── seeds
   ├── snapshots
   └── tests
  ```
Create a connection profile on your local machine. The default location is `~/.dbt/profiles.yml`

Next, [configure connection](dbt_adbs_test_project) related parameters and test if dbt connection works using dbt debug command

```text
dbt debug
   os info: macOS-11.6-x86_64-i386-64bit
   Using profiles.yml file at ~/.dbt/profiles.yml
   Using dbt_project.yml file at /dbt_oracle_test_project/dbt_project.yml
   Configuration:
     profiles.yml file [OK found and valid]
     dbt_project.yml file [OK found and valid]
   Required dependencies:
    - git [OK found]
   Connection:
     user: dbt_test
     database: ga01d76d2ecd5e0_db202112221108
     schema: dbt_test
     protocol: tcps
     host: adb.us-ashburn-1.oraclecloud.com
     port: 1522
     service: ga01d76d2ecd5e0_db202112221108_high.adb.oraclecloud.com
     connection_string: None
     shardingkey: []
     supershardingkey: []
     cclass: None
     purity: None
     Connection test: [OK connection ok]

   All checks passed!
```

## Changes added in this release (v1.0.0) <a name='changes-in-this-release'></a>

### Python versions
- Python 3.6, 3.7, 3.8 and 3.9 are supported.
- Removed support for [Python 3.5](https://www.python.org/downloads/release/python-3510/). Python 3.5 reached end-of-life in September 2020. Previous releases of `dbt-oracle` supported Python 3.5

### Enhancements <a name ='ch-features'></a>
- Following dependencies are upgraded
  - `cx_Oracle v8.3.0`
  - `dbt-core v1.0.4`
- Following development dependencies are removed
  - `watchdog`
  - `bumpversion`
  - `flake8`
  - `docutils`
  - `Sphinx`
- Added conditional dependency on `dataclasses` package for Python 3.6.
  `dataclasses` package was included in the standard library from Python 3.7
- Fallback to dbt-core `v0.21.1` for Python 3.6
- Added support to connect to a shard
- Added support for Database Resident Connection Pooling (DRCP)
- Remove hardcoded configurations. Configurations should be specified using environment variables and follow the prefix pattern `DBT_ORACLE_*`
- [PEP-517](https://www.python.org/dev/peps/pep-0517/) and [PEP-518](https://www.python.org/dev/peps/pep-0518/) compliant build system.
  - Introduced [pyproject.toml](pyproject.toml) file is used to specify build dependencies.
  - Modified [setup.py](setup.py) and [setup.cfg](setup.cfg) to define dynamic and static metadata respectively.
- tox automation to test the adapter plugin for Python versions 3.6, 3.7, 3.8 and 3.9


### Fixes <a name='ch-fixes'></a>
- Fix: **ORA-12537** for OracleConnectionMethod.HOST
- Fix: Generic tests and singular tests. Introduced macro `oracle__get_test_sql` and changed macro signatures in `schema_tests.sql`
- Fix: tests/oracle.dbtspec::test_dbt_snapshot_strategy_check_cols - **ORA-00942**: table or view does not exist
- Fix: tests/oracle.dbtspec::test_dbt_ephemeral_data_tests - **ORA-32034**: unsupported use of WITH clause
- Fix: **ORA-00933**: SQL command not properly ended raised in https://github.com/techindicium/dbt-oracle/issues/26
- Fix: Return an object of type `AdapterResponse` in adapter's `get_response(cls, cursor)` method. Cursor's rowcount attribute is included in the `AdapterResponse`
- Commented the method `list_relations_without_caching` in `dbt/adapters/oracle/impl.py`

### Integration Testing with Autonomous Database Service (ADBS) <a name='ch-integration-testing'></a>

The test project `dbt_adbs_test_project` can be used to perform integration testing with Oracle's Autonomous Database Cloud Service.
Following features are tested
- View materialization
- Table materialization
- Ephemeral materialization
- Incremental materialization
- Snapshots
- Generic Tests - Not null, Accepted values, Unique and Relationships
- Singular Tests
- Seed
- Data Sources
- Analyses
- Operations
- Document Generation and Serving

## Upcoming features <a name ='upcoming-features'></a>

We plan to support the following

- Partitioning; A partitioned table is easier to manage and decreases latency and cost when querying large tables.
- External Tables; Staging data from external sources i.e. OCI Object Store or S3

## Documentation [TODO] <a name='documentation-todo'></a>
Link to the homepage - https://oracle.github.io/dbt-oracle

Link to documentation - https://dbt-oracle.readthedocs.io

### Features <a name='features'></a>

- Connection to Oracle Autonomous Database
  - OracleConnectionMethod.TNS
  - OracleConnectionMethod.HOST
  - OracleConnectionMethod.CONNECTION_STRING
- Table materialization
- View materialization
- Incremental materialization
- Ephemeral materialization
- Seeds
- Sources
- Custom data tests
- Docs generate
- Snapshots
- Exposures
- Oracle Adapter specific custom configurations


## Contributing <a name='contributing'></a>
This project welcomes contributions from the community. Before submitting a pull request, please review our [contribution guide](CONTRIBUTING.md).

## Security <a name='security'></a>
Please consult the [security guide](SECURITY.md) for our responsible security vulnerability disclosure process.

## License <a name='license'></a>
dbt-oracle is licensed under Apache 2.0 License which you can find [here](LICENSE.txt)
