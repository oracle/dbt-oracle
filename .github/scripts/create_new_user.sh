#!/bin/bash

set -Exeuo pipefail

# Parameters
DB_USER="${1}"
ADMIN_PASSWORD="${2}"
DB_PASSWORD="${3}"

# Create the user through the ADB administrator account.
sqlplus -s "admin/${ADMIN_PASSWORD}@localhost:1521/myatp" << EOF
   -- Exit on any errors
   WHENEVER SQLERROR EXIT SQL.SQLCODE
   CREATE USER ${DB_USER} IDENTIFIED BY "${DB_PASSWORD}" QUOTA UNLIMITED ON DATA;
   GRANT CONNECT, CONSOLE_DEVELOPER, DWROLE, RESOURCE TO ${DB_USER};
   exit;
EOF
