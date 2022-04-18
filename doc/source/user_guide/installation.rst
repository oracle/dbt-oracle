.. _installation:

***************************
dbt-oracle Installation
***************************

Overview
========

To use dbt-oracle you need

- Python 3.6 or higher. It is strongly recommended to use Python 3.7+ to get access to latest dbt features

- Oracle Client libraries. These can be from the free `Oracle Instant Client
  <https://www.oracle.com/database/technologies/instant-client.html>`__, from a
  full Oracle Client installation, or from those included in Oracle Database if
  Python is on the same machine as the database. Use the latest client possible: Oracle's standard client-server
  version interoperability allows connection to both older and newer databases.

- An Oracle Database, either local or remote.

Dependencies
==================================

dbt-oracle depends on the following 3 python packages.

* dbt-core
    * Open source framework for data transformation
    * Jinja Templating and core SQL compilation logic
    * The latest version of dbt-core is preferred
    * For Python 3.6, pip will fallback to dbt-core v0.21.0

* cx-Oracle
    * Python driver for Oracle database
    * Oracle client libraries should be installed on the system. For details check `cx_Oracle installation <https://cx-oracle.readthedocs.io/en/latest/user_guide/installation.html>`__

* dataclasses; python_version < '3.7'
    * This is conditional dependency and required only for Python 3.6

The cx_Oracle module loads Oracle Client libraries which communicate
over Oracle Net to an existing database.  Oracle Net is not a separate
product: it is how the Oracle Client and Oracle Database communicate.

Installation
==================================

- Install `Python <https://www.python.org/downloads>`__ 3, if not already
  available.

- Install dbt-oracle from `PyPI
  <https://pypi.org/project/cx-Oracle/>`__ with:

  .. code-block:: shell

      python -m pip install dbt-oracle --upgrade

Support
=======
dbt-oracle will provide support for the following

* Python versions 3.6, 3.7, 3.8 and 3.9
* Autonomous Database versions 19c and 21c
* OS
    * Linux
    * MacOS
    * Windows
