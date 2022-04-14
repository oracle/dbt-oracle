.. _introduction:

**************************
Introduction to dbt-oracle
**************************
dbt (data build tool) adapter for the Oracle database.
dbt-oracle contains all code to enable dbt to work with Oracle's Autonomous Database.


What is dbt?
---------------
dbt stands for data build tool (dbt) and is a trademark of dbt Labs, Inc. The intended users of the tool are Data Analysts, Data Engineers,  BI professionals or anyone who knows SQL
It does the T in ELT (Extract, Load, Transform) and to work with dbt you need a copy of your data already loaded in your warehouse.

One way to think of dbt is an orchestration layer which sits on top of your data warehouse

.. figure:: /images/dbt_data_flow.png


* With dbt, you can express all transforms with SQL select
* No need to write boilerplate code
* Idempotence; rerun models
* All transformation code is accessible and can be version controlled.
* Use of ref() function select * from {{ ref('MODEL_NAME')}}
* dbt automatically resolves dependencies in between models and builds a Directed Acyclic Graph (DAG). Each path in the DAG can be independently executed using multiple threads.
* Interpolates the name of database schema
* Includes a built-in testing framework to ensure model accuracy
* Generate documentation for your project and render it as a website.
* Use macros to write reusable SQL


Getting Started
---------------

Install dbt-oracle using the :ref:`installation <installation>` steps.

Create a dbt project for oracle database using the `dbt init` command. The init command is interactive and will help you get started with a new project.

`dbt init` will:

* ask you the name of the project
* ask you the database adapter you are using i.e. oracle
* prompt to specify necessary connection details

This example shows initialization of test project `dbt_oracle_test_project`

.. code-block:: text
   :emphasize-lines: 1, 3, 6, 9-17

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

Then it will:

* Create a new folder with project name and sample files to get you started

.. code-block:: text

   ├── README.md
   ├── analyses
   ├── dbt_project.yml
   ├── macros
   ├── models
   │   └── example
   ├── seeds
   ├── snapshots
   └── tests

   7 directories, 2 files

* Create a connection profile on your local machine. The default location is `~/.dbt/profiles.yml`

Next, configure connection related parameters and test if dbt connection works using dbt debug command

.. code-block:: text
   :emphasize-lines: 1, 3-6, 9-17

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
