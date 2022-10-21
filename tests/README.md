# Testing

# Table of contents

- [Environment Variables](#environment-variables)
- [Adapter Plugin Tests](#adapter-plugin-tests)
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
