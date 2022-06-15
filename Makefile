# Configuration variables
VERSION=1.0.3rc1
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


# Target to test a dbt-oracle package from PyPI.
adbs_pypi_test: clean_venv
	${PYTHON_3} -m venv ${VENV_DIR}
	${VENV_DIR}/bin/pip install dbt-oracle==${VERSION}
	cd dbt_adbs_test_project && ${VENV_DIR}/bin/dbt --version
	cd dbt_adbs_test_project && ${VENV_DIR}/bin/dbt debug --profiles-dir ./
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
	cd dbt_adbs_test_project && ${VENV_DIR}/bin/dbt clean --profiles-dir ./
