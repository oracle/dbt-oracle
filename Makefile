# Configuration variables
VERSION=1.3.1
PROJ_DIR?=$(shell pwd)
VENV_DIR?=${PROJ_DIR}/.bldenv
BUILD_DIR=${PROJ_DIR}/build
DIST_DIR=${PROJ_DIR}/dist
PYTHON_3=python3.8


clean_venv:
	rm -fr ${VENV_DIR}

clean: clean_venv
	rm -fr ${DIST_DIR}
	rm -fr ${BUILD_DIR}

wheel: clean
	${PYTHON_3} -m venv ${VENV_DIR}
	${VENV_DIR}/bin/pip install --upgrade wheel dataclasses build
	${VENV_DIR}/bin/python3 -m build

# Target to test dbt-oracle package in development environment.
# This builds a wheel pkg from source in the current project directory and tests all dbt functionalities.
adbs_local_env_test: wheel clean_venv
	${PYTHON_3} -m venv ${VENV_DIR}
	${VENV_DIR}/bin/pip install ${DIST_DIR}/dbt_oracle-${VERSION}-py3-none-any.whl
	cd dbt_adbs_test_project && ${VENV_DIR}/bin/dbt --version
	cd dbt_adbs_test_project && ${VENV_DIR}/bin/dbt debug --profiles-dir ./
	cd dbt_adbs_test_project && ${VENV_DIR}/bin/dbt deps --profiles-dir ./
	cd dbt_adbs_test_project && ${VENV_DIR}/bin/dbt run-operation drop_schema --args 'relation: ${DBT_ORACLE_SCHEMA}' --profiles-dir ./
	cd dbt_adbs_test_project && ${VENV_DIR}/bin/dbt deps --profiles-dir ./
	cd dbt_adbs_test_project && ${VENV_DIR}/bin/dbt seed --profiles-dir ./
	cd dbt_adbs_test_project && ${VENV_DIR}/bin/dbt run --profiles-dir ./
	cd dbt_adbs_test_project && ${VENV_DIR}/bin/dbt test --profiles-dir ./
	cd dbt_adbs_test_project && ${VENV_DIR}/bin/dbt test --profiles-dir ./
	cd dbt_adbs_test_project && ${VENV_DIR}/bin/dbt run --profiles-dir ./
	cd dbt_adbs_test_project && ${VENV_DIR}/bin/dbt snapshot --profiles-dir ./
	cd dbt_adbs_test_project && ${VENV_DIR}/bin/dbt snapshot --profiles-dir ./
	cd dbt_adbs_test_project && ${VENV_DIR}/bin/dbt docs generate --profiles-dir ./
	cd dbt_adbs_test_project && ${VENV_DIR}/bin/dbt run-operation drop_schema --args 'relation: ${DBT_ORACLE_SCHEMA}' --profiles-dir ./
	cd dbt_adbs_test_project && ${VENV_DIR}/bin/dbt clean --profiles-dir ./


# Target to test a dbt-oracle package from PyPI.
# This installs a dbt-oracle from PyPI and tests all dbt functionalities
adbs_pypi_test: clean_venv
	${PYTHON_3} -m venv ${VENV_DIR}
	${VENV_DIR}/bin/pip install dbt-oracle==${VERSION}
	cd dbt_adbs_test_project && ${VENV_DIR}/bin/dbt --version
	cd dbt_adbs_test_project && ${VENV_DIR}/bin/dbt debug --profiles-dir ./
	cd dbt_adbs_test_project && ${VENV_DIR}/bin/dbt deps --profiles-dir ./
	cd dbt_adbs_test_project && ${VENV_DIR}/bin/dbt run-operation drop_schema --args 'relation: ${DBT_ORACLE_SCHEMA}' --profiles-dir ./
	cd dbt_adbs_test_project && ${VENV_DIR}/bin/dbt seed --profiles-dir ./
	cd dbt_adbs_test_project && ${VENV_DIR}/bin/dbt run --profiles-dir ./
	cd dbt_adbs_test_project && ${VENV_DIR}/bin/dbt test --profiles-dir ./
	cd dbt_adbs_test_project && ${VENV_DIR}/bin/dbt test --profiles-dir ./
	cd dbt_adbs_test_project && ${VENV_DIR}/bin/dbt run --profiles-dir ./
	cd dbt_adbs_test_project && ${VENV_DIR}/bin/dbt snapshot --profiles-dir ./
	cd dbt_adbs_test_project && ${VENV_DIR}/bin/dbt snapshot --profiles-dir ./
	cd dbt_adbs_test_project && ${VENV_DIR}/bin/dbt docs generate --profiles-dir ./
	cd dbt_adbs_test_project && ${VENV_DIR}/bin/dbt run-operation drop_schema --args 'relation: ${DBT_ORACLE_SCHEMA}' --profiles-dir ./
	cd dbt_adbs_test_project && ${VENV_DIR}/bin/dbt clean --profiles-dir ./
