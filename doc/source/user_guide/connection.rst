.. _connection:

****************************************************
Connecting to Oracle Autonomous Database
****************************************************

Overview
========

Oracle Autonomous Database is the world’s first autonomous data management in the cloud to deliver automated patching, upgrades, and tuning—including performing all routine database maintenance tasks while the system is running - without human intervention. This new autonomous database cloud is self-driving, self-securing, and self-repairing, which helps to eliminate manual database management and human errors.

To test dbt with Autonomous Database, you can start with OCI's Always Free Autonomous Database. The database is provided free of charge with the following settings.

* Processor: 1 Oracle CPU processor
* Database Storage: 20 GB storage
* Workload Type could be either ATP (Autonomous Transaction Processing) or ADW (Autonomous Data Warehouse)

Connection specific environment variables
=========================================

Define the following variables from where you can source them before running dbt commands. For example, in `~/.bashrc` file

.. code-block:: bash

    # cx_oracle needs lib_dir parameter pointing to the folder
    # containing the libraries from an unzipped Instant Client Basic or Basic Light package.
    # If lib_dir is not passed client libraries are looked for in the Operating system search path
    # or set in the following environment variables.
    DYLD_LIBRARY_PATH # For MacOS
    LD_LIBRARY_PATH # For Linux

    # For ADBS, cx_oracle will need the path to the folder
    # containing client wallet, sqlnet.ora and tnsnames.ora
    TNS_ADMIN

    # Database connection config
    DBT_ORACLE_USER
    DBT_ORACLE_HOST
    DBT_ORACLE_PORT
    DBT_ORACLE_SERVICE
    DBT_ORACLE_PASSWORD
    DBT_ORACLE_DATABASE
    DBT_ORACLE_SCHEMA

dbt project configuration
=========================
Every dbt project needs a `dbt_project.yml` file — this is how dbt knows a directory is a dbt project. It also contains important information that tells dbt how to operate on your project.
Specify the connection profile as shown below

.. code-block:: yaml
    :emphasize-lines: 3

    name: dbt_oracle_test_project
    config-version: 2
    version: 1.0
    profile: dbt_test
    analysis-paths: ['analysis']
    test-paths: ['test']

    quoting:
      database: false
      identifier: false
      schema: false

    # seed configurations
    seeds:
        dbt_oracle_test_project:
            quote_columns: false

    # snapshot configurations
    snapshots:
        dbt_oracle_test_project:
            target_schema: "{{ env_var('DBT_ORACLE_USER') }}"

    on-run-start:
        - "select 'hook start' from dual"

    on-run-end:
        - "select 'hook ended' from dual"

Connection Profile Parameters
=============================

* type
   * description - type of dbt adapter
   * value - oracle

* user
   * description - Oracle database username
   * value - Value can be set in environment variable DBT_ORACLE_USER

* pass
   * description - Oracle database password
   * value - Value can be set in environment variable DBT_ORACLE_PASSWORD

* protocol
   * description - tcp or tcps

* host
   * description - Oracle Autonomous Database host
   * value - Value can be set in environment variable DBT_ORACLE_HOST
   * example - adb.us-ashburn-1.oraclecloud.com

* port
   * description - Oracle Autonomous Database port (1521 or 1522)
   * value - Value can be set in environment variable DBT_ORACLE_PORT

* service
   * description - Service name as defined in tnsnames.ora
   * value - Value can be set in environment variable DBT_ORACLE_SERVICE
   * example - <databasename>_high.adb.oraclecloud.com

* database
   * description - database name
   * value - Value can be set in environment variable DBT_ORACLE_DATABASE

* schema
   * description - database schema; For Oracle this is the same as database user
   * value - Value can be set in environment variable DBT_ORACLE_SCHEMA

* shardingkey
   * description - List of sharding keys to connect to shard

* supershardingkey
    * description - List of super-sharding keys to connect to shard

* cclass
    * description - Connectivity class to enable Database Resident Connection Pooling (DRCP)

* purity
    * description - self|new|default

Connection Profile
==================


.. code-block:: yaml

   dbt_test:
       target: "{{ env_var('DBT_TARGET', 'dev') }}"
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

