# dbt-oracle

[![PyPI version](https://badge.fury.io/py/dbt-oracle.svg)](https://pypi.python.org/pypi/dbt-oracle)
![Build](https://github.com/oracle/dbt-oracle/actions/workflows/oracle-xe-adapter-tests.yml/badge.svg)

dbt "adapters" are responsible for adapting dbt's functionality to a given database. `dbt-oracle` implements dbt functionalities for the Oracle database. To learn more about building adapters, check
https://docs.getdbt.com/docs/contributing/building-a-new-adapter

> Prior to version 1.0.0, dbt-oracle was created and maintained by [Indicium](https://indicium.tech/) on [their GitHub repo](https://github.com/techindicium/dbt-oracle). Contributors in this repo are credited for laying the groundwork and maintaining the adapter till version 0.4.3.
From version 1.0.0, dbt-oracle is maintained and distributed by Oracle.

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
```sql
--models/sales_internet_channel.sql
{{ config(materialized='table') }}
WITH sales_internet AS (
       SELECT * FROM {{ source('sh_database', 'sales') }}
       WHERE channel_id = 4 )
SELECT * FROM sales_internet
```
dbt compiles the above SQL template to run the below DDL statement.
```sql
CREATE TABLE dbt_test.sales_internet_channel AS
WITH sales_internet AS (
         SELECT * from sh.sales
         WHERE channel_id = 4 )
SELECT * FROM sales_internet
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

`dbt-core`

  - Open source framework for data transformation
  - Jinja Templating and core SQL compilation logic
  - Latest version of dbt-core is preferred; From version 1.0.0, dbt-core supports Python 3.7 or higher
  - For Python 3.6, pip will fallback to version 0.21.1 of dbt-core

`cx-Oracle`
 - Python driver for Oracle database
 - Oracle client libraries should be installed on the system. For details check, https://cx-oracle.readthedocs.io/en/latest/user_guide/installation.html

`dataclasses; python_version < '3.7'`
 - dataclasses package was introduced in the standard Python library from Python 3.7. This is conditional dependency and required only for Python 3.6
 
## Getting Started <a name='getting-started'></a>

Create a dbt project for oracle database using the `dbt init` command. The init command is interactive and will help you get started with a new project.

`dbt init` will:

* ask you the name of the project
* ask you the database adapter you are using i.e. oracle
* prompt to specify necessary connection details

This example shows initialization of test project `dbt_oracle_test_project`

```text
>> dbt init

Running with dbt=1.0.4
Enter a name for your project (letters, digits, underscore): dbt_oracle_test_project
Which database would you like to use?
[1] oracle
  Enter a number: 1
  protocol (tcp or tcps) [tcps]: 
  host (adb.<oci-region>.oraclecloud.com) [{{ env_var('DBT_ORACLE_HOST') }}]: 
  port [1522]: 
  user [{{ env_var('DBT_ORACLE_USER') }}]: 
  password [{{ env_var('DBT_ORACLE_PASSWORD') }}]: 
  service (service name in tnsnames.ora) [{{ env_var('DBT_ORACLE_SERVICE') }}]: 
  dbname (database name in which dbt objects should be created) [{{ env_var('DBT_ORACLE_DATABASE') }}]: 
  schema (database schema in which dbt objects should be created) [{{ env_var('DBT_ORACLE_SCHEMA') }}]: 
  threads (1 or more) [1]: 4
Profile dbt_oracle_test_project written to ~/.dbt/profiles.yml using target's profile_template.yml and your supplied values. Run 'dbt debug' to validate the connection.
Your new dbt project "dbt_oracle_test_project" was created!

```

Then dbt init command will:

1. Create the following folder with project name and sample files to get you started
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
2. Create a connection profile on your local machine. The default location is `~/.dbt/profiles.yml`

    Next step, [configure connection][1] related parameters and test if dbt connection works using dbt debug command
    
    ```text
    >> dbt debug
     
    os info: macOS-11.6-x86_64-i386-64bit
       Using profiles.yml file at ~/.dbt/profiles.yml
       Using dbt_project.yml file at /dbt_oracle_test_project/dbt_project.yml
       Configuration:
        profiles.yml file [OK found and valid]
        dbt_project.yml file [OK found and valid]
       Required dependencies:
       - git [OK found]
       Connection:
        user: ***
        database: ga01d76d2ecd5e0_db202112221108
        schema: ***
        protocol: tcps
        host: adb.us-ashburn-1.oraclecloud.com
        port: 1522
        service: <service_name>_high.adb.oraclecloud.com
        connection_string: None
        shardingkey: []
        supershardingkey: []
        cclass: None
        purity: None
        Connection test: [OK connection ok]
    
       All checks passed!
    ```

## Documentation [TODO] <a name='documentation-todo'></a>
Link to the homepage - https://oracle.github.io/dbt-oracle

Link to documentation - https://dbt-oracle.readthedocs.io

## Contributing <a name='contributing'></a>
This project welcomes contributions from the community. Before submitting a pull request, please review our [contribution guide][2].

## Security <a name='security'></a>
Please consult the [security guide][3] for our responsible security vulnerability disclosure process.

## License <a name='license'></a>
dbt-oracle is licensed under Apache 2.0 License which you can find [here][4]

[1]: https://github.com/oracle/dbt-oracle/blob/main/dbt_adbs_test_project/profiles.yml
[2]: https://github.com/oracle/dbt-oracle/blob/main/CONTRIBUTING.md
[3]: https://github.com/oracle/dbt-oracle/blob/main/SECURITY.md
[4]: https://github.com/oracle/dbt-oracle/blob/main/LICENSE.txt
