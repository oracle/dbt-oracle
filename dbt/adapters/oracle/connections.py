"""
Copyright (c) 2022, Oracle and/or its affiliates.
Copyright (c) 2020, Vitor Avancini

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

     https://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
"""
from typing import List, Optional, Tuple, Any, Dict, Union
from contextlib import contextmanager
from dataclasses import dataclass, field
import enum
import time

import dbt.exceptions
from dbt.adapters.base import Credentials
from dbt.adapters.sql import SQLConnectionManager
from dbt.contracts.connection import AdapterResponse
from dbt.events import AdapterLogger

from dbt.adapters.oracle.connection_helper import oracledb, SQLNET_ORA_CONFIG

logger = AdapterLogger("oracle")


class OracleConnectionMethod(enum.Enum):
    HOST = 1
    TNS = 2
    CONNECTION_STRING = 3


@dataclass
class OracleAdapterCredentials(Credentials):
    """Collect Oracle credentials

    An OracleConnectionMethod is inferred from the combination
    of parameters profiled in the profile.
    """
    # Mandatory required arguments.
    user: str
    password: str
    # Specifying database is optional
    database: Optional[str]

    # OracleConnectionMethod.TNS
    tns_name: Optional[str] = None

    # OracleConnectionMethod.HOST
    protocol: Optional[str] = None
    host: Optional[str] = None
    port: Optional[Union[str, int]] = None
    service: Optional[str] = None

    # OracleConnectionMethod.CONNECTION_STRING
    connection_string: Optional[str] = None

    # shardingkey and supershardingkey is a list
    shardingkey: Optional[List[str]] = field(default_factory=list)
    supershardingkey: Optional[List[str]] = field(default_factory=list)

    # Database Resident Connection Pooling (DRCP)
    cclass: Optional[str] = None
    purity: Optional[str] = None


    _ALIASES = {
        'dbname': 'database',
        'pass': 'password',
    }

    @property
    def type(self):
        return 'oracle'

    @property
    def unique_field(self):
        return self.database

    def _connection_keys(self) -> Tuple[str]:
        """
        List of keys to display in the `dbt debug` output. Omit password.
        """
        return (
            'user', 'database', 'schema',
            'protocol', 'host', 'port', 'tns_name',
            'service', 'connection_string',
            'shardingkey', 'supershardingkey',
            'cclass', 'purity'
        )

    @classmethod
    def __pre_deserialize__(cls, data: Dict[Any, Any]) -> Dict[Any, Any]:
        # If database is not defined as adapter credentials
        data = super().__pre_deserialize__(data)
        if "database" not in data:
            data["database"] = None
        return data

    def connection_method(self) -> OracleConnectionMethod:
        """Return an OracleConnecitonMethod inferred from the configuration"""
        if self.connection_string:
            return OracleConnectionMethod.CONNECTION_STRING
        elif self.host:
            return OracleConnectionMethod.HOST
        else:
            return OracleConnectionMethod.TNS

    def get_dsn(self) -> str:
        """Create dsn for cx_Oracle for either any connection method

        See https://cx-oracle.readthedocs.io/en/latest/user_guide/connection_handling.html"""

        method = self.connection_method()
        if method == OracleConnectionMethod.TNS:
            return self.tns_name
        if method == OracleConnectionMethod.CONNECTION_STRING:
            return self.connection_string

        # Assume host connection method OracleConnectionMethod.HOST and necessary parameters are defined
        return f'{self.protocol}://{self.host}:{self.port}/{self.service}'


class OracleAdapterConnectionManager(SQLConnectionManager):
    TYPE = 'oracle'

    @classmethod
    def open(cls, connection):
        if connection.state == 'open':
            logger.debug('Connection is already open, skipping open.')
            return connection
        credentials = cls.get_credentials(connection.credentials)
        method = credentials.connection_method()
        dsn = credentials.get_dsn()

        logger.debug(f"Attempting to connect using Oracle method: '{method}' "
                     f"and dsn: '{dsn}'")

        conn_config = {
            'user': credentials.user,
            'password': credentials.password,
            'dsn': dsn
        }

        if credentials.shardingkey:
            conn_config['shardingkey'] = credentials.shardingkey

        if credentials.supershardingkey:
            conn_config['supershardingkey'] = credentials.supershardingkey

        if credentials.cclass:
            conn_config['cclass'] = credentials.cclass

        if credentials.purity:
            purity = credentials.purity.lower()
            if credentials.purity == 'new':
                conn_config['purity'] = oracledb.ATTR_PURITY_NEW
            elif purity == 'self':
                conn_config['purity'] = oracledb.ATTR_PURITY_SELF
            elif purity == 'default':
                conn_config['purity'] = oracledb.ATTR_PURITY_DEFAULT

        if SQLNET_ORA_CONFIG is not None:
            conn_config.update(SQLNET_ORA_CONFIG)

        try:
            handle = oracledb.connect(**conn_config)
            connection.handle = handle
            connection.state = 'open'
        except oracledb.DatabaseError as e:
            logger.info(f"Got an error when attempting to open an Oracle "
                        f"connection: '{e}'")
            connection.handle = None
            connection.state = 'fail'

            raise dbt.exceptions.FailedToConnectException(str(e))

        return connection

    @classmethod
    def cancel(cls, connection):
        connection_name = connection.name
        oracle_connection = connection.handle

        logger.info("Cancelling query '{}' ".format(connection_name))

        try:
            oracledb.Connection.close(oracle_connection)
        except Exception as e:
            logger.error('Error closing connection for cancel request')
            raise Exception(str(e))

        logger.info("Canceled query '{}'".format(connection_name))

    @classmethod
    def get_status(cls, cursor):
        # Do oracle cx has something for this? could not find it
        return 'OK'

    @classmethod
    def get_response(cls, cursor):
        # number of rows fetched for a SELECT statement or
        # have been affected by INSERT, UPDATE, DELETE and MERGE statements
        return AdapterResponse(rows_affected=cursor.rowcount,
                               _message='OK')

    @contextmanager
    def exception_handler(self, sql):
        try:
            yield

        except oracledb.DatabaseError as e:
            logger.info('Oracle error: {}'.format(str(e)))

            try:
                # attempt to release the connection
                self.release()
            except oracledb.Error:
                logger.info("Failed to release connection!")
                pass

            raise dbt.exceptions.DatabaseException(str(e).strip()) from e

        except Exception as e:
            logger.info("Rolling back transaction.")
            self.release()
            if isinstance(e, dbt.exceptions.RuntimeException):
                # during a sql query, an internal to dbt exception was raised.
                # this sounds a lot like a signal handler and probably has
                # useful information, so raise it without modification.
                raise e

            raise dbt.exceptions.RuntimeException(e) from e

    @classmethod
    def get_credentials(cls, credentials):
        return credentials

    def add_query(
        self,
        sql: str,
        auto_begin: bool = True,
        bindings: Optional[Any] = {},
        abridge_sql_log: bool = False
    ) -> Tuple[oracledb.Connection, Any]:
        connection = self.get_thread_connection()
        if auto_begin and connection.transaction_open is False:
            self.begin()

        logger.debug('Using {} connection "{}".'
                     .format(self.TYPE, connection.name))

        with self.exception_handler(sql):
            if abridge_sql_log:
                log_sql = '{}...'.format(sql[:512])
            else:
                log_sql = sql

            logger.debug(f'On {connection.name}: f{log_sql}')
            pre = time.time()

            cursor = connection.handle.cursor()
            cursor.execute(sql, bindings)
            connection.handle.commit()
            logger.debug(f"SQL status: {self.get_status(cursor)} in {(time.time() - pre)} seconds")
            return connection, cursor

    def add_begin_query(self):
        connection = self.get_thread_connection()
        cursor = connection.handle.cursor
        return connection, cursor
