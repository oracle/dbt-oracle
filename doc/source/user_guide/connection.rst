.. _connection:

****************************************************
Connecting to Oracle Autonomous Database
****************************************************

Overview
========

Oracle Autonomous Database is the world’s first autonomous data management in the cloud to deliver automated patching, upgrades, and tuning—including performing all routine database maintenance tasks while the system is running - without human intervention. This new autonomous database cloud is self-driving, self-securing, and self-repairing, which helps to eliminate manual database management and human errors.

To test dbt with Autonomous Database, you can start with OCI's `Always Free Autonomous Database <https://docs.oracle.com/en-us/iaas/Content/Database/Concepts/adbfreeoverview.htm>`__. The database is provided free of charge with the following settings.

* 1 Oracle CPU processor
* 20 GB storage
* Workload Type could be either ATP (Autonomous Transaction Processing) or ADW (Autonomous Data Warehouse)

The database also provides a read-only Sales History data set. dbt models can directly use source tables in `sh` schema without any additional steps


Client Credential Wallet
========================

If your Autonomous Database instance is configured to allow only mTLS connections then you will need the client credentials wallet with the following files

* tnsnames.ora
* sqlnet.ora
* cwallet.sso
* ewallet.p12

After downloading the wallet, put the unzipped wallet files in a secure directory and set the TNS_ADMIN environment variable to that directory name.
Next, edit the `sqlnet.ora` file to point to the wallet directory


.. code-block:: text

   WALLET_LOCATION = (SOURCE = (METHOD = file) (METHOD_DATA = (DIRECTORY="/path/to/wallet/directory")))
   SSL_SERVER_DN_MATCH=yes

References
^^^^^^^^^^

* `Download client credential wallet <https://docs.oracle.com/en/cloud/paas/autonomous-database/adbsa/connect-download-wallet.html#GUID-B06202D2-0597-41AA-9481-3B174F75D4B1>`__
* `Connect using mTLS <https://docs.oracle.com/en/cloud/paas/autonomous-database/adbsa/connecting-nodejs.html#GUID-AB1E323A-65B9-47C4-840B-EC3453F3AD53>`__
* `Connect using TLS without a wallet <https://docs.oracle.com/en/cloud/paas/autonomous-database/adbsa/connecting-nodejs-tls.html#GUID-B3809B88-D2FB-4E08-8F9B-65A550F93A07>`__

Connection specific environment variables
=========================================

Define the following environment variables.

.. code-block:: bash

    # cx_oracle needs lib_dir parameter pointing to the folder
    # containing the libraries from an unzipped Instant Client Basic or Basic Light package.
    # If lib_dir is not passed client libraries are looked for in the Operating system search path
    # or set in the following environment variables.
    DYLD_LIBRARY_PATH # For MacOS
    LD_LIBRARY_PATH # For Linux

    # cx_oracle will need the path to the folder
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
Specify the connection profile in `dbt_project.yml` file as shown below

.. code-block:: yaml
    :emphasize-lines: 4

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


Connection Profile
==================

Below is an example of `dbt_test` connection profile referred in `dbt_project.yml` as shown above

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

Connection Profile Parameters
=============================

type
^^^^
* Description - The type of dbt adapter
* Value - `oracle`

user
^^^^
* Description - Oracle database username
* Value - Value can be set in environment variable `DBT_ORACLE_USER`

pass
^^^^
* Description - Oracle database password
* Value - Value can be set in environment variable `DBT_ORACLE_PASSWORD`

protocol
^^^^^^^^
* Description - Client-Server communication protocol i.e. TCP/IP or TCP/IP with SSL
* Value - `tcp` or `tcps`

host
^^^^
* Description - Oracle Database host
* Value - Value can be set in environment variable `DBT_ORACLE_HOST`
* Example - adb.us-ashburn-1.oraclecloud.com

port
^^^^
* Description - Oracle Database port (1521 or 1522)
* Value - Value can be set in environment variable `DBT_ORACLE_PORT`

service
^^^^^^^
* Description - Service name as defined in tnsnames.ora
* Value - Value can be set in environment variable `DBT_ORACLE_SERVICE`
* Example - <databasename>_high.adb.oraclecloud.com

database
^^^^^^^^
* Description - Database name
* Value - Value can be set in environment variable `DBT_ORACLE_DATABASE`

schema
^^^^^^
* Description - database schema; For Oracle this is the same as database user
* Value - Value can be set in environment variable `DBT_ORACLE_SCHEMA`

shardingkey
^^^^^^^^^^^
* Description - List of sharding keys to connect to a shard

supershardingkey
^^^^^^^^^^^^^^^^
* Description - List of super-sharding keys to connect to a shard

cclass
^^^^^^
* Description - Connectivity class to use for  Database Resident Connection Pooling (DRCP). When a pooled session has a connection class the session is not shared outside the connection class

purity
^^^^^^
* Description - Session purity specifies whether an application can reuse a pooled session (self) or must use a new session (new)
* Value - Must be one of `self`, `new`, `default`