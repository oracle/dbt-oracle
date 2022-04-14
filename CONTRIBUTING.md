# Contributing

We welcome your contributions! There are multiple ways to contribute.

## Issues

For bugs or enhancement requests, please file a GitHub issue unless it's security related. When filing a bug remember that the better written the bug is, the more likely it is to be fixed. If you think you've found a security vulnerability, do not raise a GitHub issue and follow the instructions on our Security Policy.

## Contributing Code

We welcome your code contributions. To get started, you will need to sign the [Oracle Contributor Agreement (OCA)](https://oca.opensource.oracle.com/).

For pull requests to be accepted, the bottom of your commit message must have the following line using the name and e-mail address you used for the OCA.

```text
Signed-off-by: Your Name <you@example.org>
```

This can be automatically added to pull requests by committing with:

```text
git commit --signoff
```

Only pull requests from committers that can be verified as having signed the OCA can be accepted.

## Pull request process

1. Fork this repository
2. Create a branch in your fork to implement the changes. We recommend using the issue number as part of your branch name, e.g. 1234-fixes
3. Ensure that any documentation is updated with the changes that are required by your fix.
4. Ensure that any samples are updated if the base image has been changed.
5. Submit the pull request. Do not leave the pull request blank. Explain exactly what your changes are meant to do and provide simple steps on how to validate your changes. Ensure that you reference the issue you created as well.
6. We will review your PR before it is merged.

## Setting the development environment

Clone this repo in a directory where you would like to work from

```bash
git clone ssh://git@github.com:oracle/dbt-oracle.git
```

Create a virtual environment
```bash
python3 -m venv .db-oracle-env
source .db-oracle-env/bin/activate
```

Install development requirements
```bash
pip install --upgrade pip
pip install -r requirements_dev,txt
```

Install core dependencies
```bash
pip install -r requirements.txt
```

Run the following command.
```bash
python3 setup.py develop
```
This command allows you to deploy the project’s source for use in one or more “staging areas” where it will be available for importing. This deployment is done in such a way that changes to the project source are immediately available in the staging area(s), without needing to run a build or install step after each change.

It creates a special `.egg-link` file in the deployment directory, that links to the source code.
And if the deployment directory is Python's site-packages directory, it will also update the
`easy-install.pth` file to include the source code, thereby making it available on `sys.path` for all programs using the Python installation

For details check - https://setuptools.pypa.io/en/latest/userguide/commands.html#develop

Once done with development, the project can be removed from the staging area using

```bash
python3 setup.py develop --uninstall
```

## Testing <a name='testing'></a>

### Environment variables <a name='environment-variables'></a>

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
    DBT_ORACLE_SERVICE
    DBT_ORACLE_PASSWORD
    DBT_ORACLE_DATABASE
    DBT_ORACLE_SCHEMA
```

### Adapter Plugin Tests <a name='adapter-plugin-tests'></a>

dbt-labs has built a package [dbt-adapter-tests](https://github.com/dbt-labs/dbt-adapter-tests) which defines a test suite for adapter plugins

It can be installed using
```bash
pip install pytest-dbt-adapter
```
The spec file [oracle.dbtspec](tests/oracle.dbtspec) lists all test sequences

To run the test cases for Python 3.7, 3.8 and 3.9 type the following command
```bash
pytest tests/oracle.dbtspec tests/test_config.py # For Python 3.7, 3.8 and 3.9

or

pytest tests/oracle_py36.dbtspect tests/test_config.py # For Python 3.6
```
All tests are passing for Python 3.7, 3.8 and 3.9
```text
tests/oracle.dbtspec::test_dbt_empty
tests/oracle.dbtspec::test_dbt_base
tests/oracle.dbtspec::test_dbt_ephemeral
tests/oracle.dbtspec::test_dbt_incremental
tests/oracle.dbtspec::test_dbt_snapshot_strategy_timestamp
tests/oracle.dbtspec::test_dbt_snapshot_strategy_check_cols
tests/oracle.dbtspec::test_dbt_schema_test
tests/oracle.dbtspec::test_dbt_data_test
tests/oracle.dbtspec::test_dbt_ephemeral_data_tests
```

Known failing test only for Python 3.6
```text
FAILED tests/oracle.dbtspec::test_dbt_empty
```


### Different Python versions <a name='different-python-versions'></a>

`tox` is a command line tool to check if the package installs correctly for different python versions. It also runs all the tests in each of the environments. Check the configuration file [tox.ini](tox.ini) for details.

To run tox, from command line type
```bash
tox
```
If all tests succeed for all python environments, you will see the below output.

```text
  py36: commands succeeded
  py37: commands succeeded
  py38: commands succeeded
  py39: commands succeeded
  congratulations :)
```
For each environment, you can also see the test runtime as summary
```text
  py36 - 12 passed, 8 warnings in 693.73s (0:11:33)
  py37 - 13 passed, 9 warnings in 673.23s (0:11:13)
  py38 - 13 passed, 9 warnings in 745.82s (0:12:25)
  py39 - 13 passed, 9 warnings in 693.90s (0:11:33)
```

## Build & Packaging <a name='build--packaging'></a>

This section explains how to build dbt-oracle package, generate the distribution archive and upload it to Python Package Index (PyPI).

[pyproject.toml](pyproject.toml) tells build tools like `pip` and `build` what is required to build the project. We use the standard `setuptools`

```toml
# pyproject.toml
[build-system]
requires = ['setuptools', 'wheel']
build-backend = "setuptools.build_meta"
```

### Configuring Metadata <a name='configuring-metadata'></a>

- Static metadata
  - [setup.cfg](setup.cfg) is a configuration file for `setuptools`. It is guaranteed to be the same everytime

- Dynamic metadata
  - [setup.py](setup.py) is the build script for `setuptools`
  - It is used to determine any items at install time. All Extension modules need to go into setup.py

### Generating distribution archives <a name='generating-distribution-archives'></a>

Run the command

```bash
python3 -m build

or

python3 setup.py bdist_wheel
```

This will generate 2 files in the `dist` folder.
The `tar.gz` file is the source archive and `.whl` is the built distribution. Newer pip versions will install the built distribution but will fall back to
source archive if needed.

```text
-rw-r--r--  1  29323 Nov 24 12:56 dbt-oracle-0.4.4.tar.gz
-rw-r--r--  1  25599 Nov 24 12:56 dbt_oracle-0.4.4-py3-none-any.whl
```

### Upload to PyPI <a name='upload-distribution-archives'></a>

Finally, the package can be uploaded to the Python Package Index (PyPI) using `twine`

Install `twine`
```bash
pip install --upgrade twine
```

Run the upload command to upload all archives in dist/*

```bash
python3 -m twine upload dist/*
```


## Code of Conduct

Follow the [Golden Rule](https://en.wikipedia.org/wiki/Golden_Rule). If you'd like more specific guidelines see the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/1/4/code-of-conduct/)
