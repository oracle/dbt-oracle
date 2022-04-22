.. _introduction:

**************************
Introduction to dbt-oracle
**************************
dbt (data build tool) adapter for the Oracle database.


What is dbt?
---------------
dbt stands for data build tool (dbt) and is a trademark of dbt Labs, Inc. The intended users of the tool are Data Analysts, Data Engineers,  BI professionals or anyone who knows SQL.
It does the T in ELT (Extract, Load, Transform) and to work with dbt you need a copy of your data already loaded in your warehouse.

One way to think of dbt is an orchestration layer which sits on top of your data warehouse

.. figure:: /images/dbt_data_flow.png

dbt-core
^^^^^^^^

`Core SQL+Jinja compilation logic`

dbt-core implements compilation logic to generate valid SQL statements for a dbt model; dbt models are written using a mix of Jinja and SQL. Below is an example

.. code-block:: sql

   --models/sales_internet_channel.sql
   {{ config(materialized='table') }}
   WITH sales_internet AS (
          SELECT * FROM {{ source('sh_database', 'sales') }}
          WHERE channel_id = 4 )
   SELECT * FROM sales_internet

It is responsible for dispatching invocation to the corresponding adapter specific implementation.
For the example above, a create table statement is generated using the adapter implementation which dbt-core invokes

.. code-block:: sql

   CREATE TABLE dbt_test.sales_internet_channel AS
   WITH sales_internet AS (
            SELECT * from sh.sales
            WHERE channel_id = 4 )
   SELECT * FROM sales_internet


`Directed Acyclic Graph (DAG)`

dbt builds a directed acyclic graph (DAG) based on the interdependencies between models – each node of the graph represents a model, and edges between the nodes are defined by `ref` functions, where a model specified in a `ref` function is recognized as a predecessor of the current model.
When dbt runs, models are executed in the order specified by the DAG

For complete list of dbt functionalities check dbt documentation

Getting Started
---------------
dbt adapters "adapt" dbt functionalities for a given database. `dbt-oracle` efficiently implements dbt functionalities for the Oracle database and seamlessly integrates with Autonomous Database

To get started, install `dbt-oracle` using the :ref:`installation <installation>` steps.

Create a dbt project using the `dbt init` command. `dbt init` command will:

* ask you the name of the project
* ask you the database adapter you are using i.e. oracle
* prompt to specify necessary connection details

The example below shows initialization of test project `dbt_oracle_test_project`

.. code-block:: text
   :emphasize-lines: 1, 4, 6-14

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

Then the `dbt init` command will:

* Create a new folder with project name and sample files to get you started

.. code-block:: text

   |-- README.md
   |-- analyses
   |-- dbt_project.yml
   |-- macros
   |-- models
   |--     |--- example
   |-- seeds
   |-- snapshots
   |-- tests

   7 directories, 2 files

* Create a connection profile on your local machine. The default location is `~/.dbt/profiles.yml`

Next, :ref:`configure connection<connection>` related parameters and validate database connection using `dbt debug` command.

If parameters are configured correctly and connection works then debug command should exit successfully.

.. code-block:: text
   :emphasize-lines: 1, 3-6, 9-17

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

