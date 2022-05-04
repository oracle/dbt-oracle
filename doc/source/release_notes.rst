:orphan:

.. _releasenotes:

dbt-oracle Release Notes
========================

Version 1.0.0 (May 2022)
^^^^^^^^^^^^^^^^^^^^^^^^

* Python versions
   * Python 3.6, 3.7, 3.8 and 3.9 are supported.
   * Removed support for Python 3.5. Python 3.5 reached end-of-life in September 2020. Previous releases of dbt-oracle supported Python 3.5
* Enhancements
   * Following dependencies are upgraded
      * cx_Oracle v8.3.0
      * dbt-core v1.0.6
   * Following development dependencies are removed
      * watchdog
      * bumpversion
      * flake8
      * docutils
      * Sphinx
   * Added conditional dependency on dataclasses package for Python 3.6. dataclasses package was included in the standard library from Python 3.7
   * Fallback to dbt-core v0.21.1 for Python 3.6
   * Added support to connect to a shard
   * Added support for Database Resident Connection Pooling (DRCP)
   * Remove hardcoded configurations. Configurations should be specified using environment variables and follow the prefix pattern DBT_ORACLE_*
   * PEP-517 and PEP-518 compliant build system.
      * Introduced pyproject.toml file to specify build dependencies.
      * Modified setup.py and setup.cfg to define dynamic and static metadata respectively.
   * tox automation to test the adapter plugin for Python versions 3.6, 3.7, 3.8 and 3.9
* Fixes
    * Fix: ORA-12537 for OracleConnectionMethod.HOST
    * Fix: Generic tests and singular tests. Introduced macro oracle__get_test_sql and changed macro signatures in schema_tests.sql
    * Fix: tests/oracle.dbtspec::test_dbt_snapshot_strategy_check_cols - ORA-00942: table or view does not exist
    * Fix: tests/oracle.dbtspec::test_dbt_ephemeral_data_tests - ORA-32034: unsupported use of WITH clause
    * Fix: ORA-00933: SQL command not properly ended raised in https://github.com/techindicium/dbt-oracle/issues/26
    * Fix: Return an object of type AdapterResponse in adapter's get_response(cls, cursor) method. Cursor's rowcount attribute is included in the AdapterResponse
    * Commented the method list_relations_without_caching in dbt/adapters/oracle/impl.py
* Integration Testing with Autonomous Database Service (ADBS)
    * The test project dbt_adbs_test_project can be used to perform integration testing with Oracle's Autonomous Database Cloud Service. Following features are tested



