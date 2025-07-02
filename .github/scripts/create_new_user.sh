#!/bin/bash

set -Exeuo pipefail

# Parameters
DB_USER="${1}"
DB_PASSWORD="${2}"
TARGET_PDB="${3:-FREEPDB1}"

# Prepare container switch statement to create user in PDB.
ALTER_SESSION_CMD="ALTER SESSION SET CONTAINER=${TARGET_PDB};"

# 11g XE does not support PDBs, set container switch statement to empty string.
ORACLE_VERSION=$(sqlplus -version | grep "Release" | awk '{ print $3 }')
if [[ "${ORACLE_VERSION}" = "11.2"* ]]; then
   ALTER_SESSION_CMD="";
fi;

# Create new user in target PDB
sqlplus -s / as sysdba << EOF
   -- Exit on any errors
   WHENEVER SQLERROR EXIT SQL.SQLCODE
   ${ALTER_SESSION_CMD}
   CREATE USER ${DB_USER} IDENTIFIED BY "${DB_PASSWORD}" QUOTA UNLIMITED ON SYSTEM;
   GRANT DB_DEVELOPER_ROLE TO ${DB_USER};
   exit;
EOF
