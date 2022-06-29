import enum
import os

import dbt.exceptions
from dbt.events import AdapterLogger

logger = AdapterLogger("oracle")


class OracleNetConfig(dict):
    """The sqlnet.ora file is only supported in the python-oracledb Thick mode.
    In Thin mode, the user can pass these as environment variables

    """

    keys = (
        'ssl_server_cert_dn',
        'ssl_server_dn_match',
        'wallet_password',
        'wallet_location',
        'expire_time',
        'https_proxy',
        'https_proxy_port',
        'retry_count',
        'retry_delay',
        'tcp_connect_timeout',
        'disable_oob'
    )

    @classmethod
    def from_env(cls):
        data = {}
        for key in OracleNetConfig.keys:
            val = os.getenv(key.upper())
            if val is not None:
                data[key] = val
        return cls(data)


class OracleDriverType(str, enum.Enum):
    """Database Driver Type"""
    THIN = "THIN"
    THICK = "THICK"
    CX_ORACLE = "CX"


SQLNET_ORA_CONFIG = None

# Set the environment variable ORA_PYTHON_DRIVER_TYPE to one of “cx”, “thin”, or “thick”:
ORA_PYTHON_DRIVER_TYPE = os.getenv('ORA_PYTHON_DRIVER_TYPE', 'cx').upper()
if ORA_PYTHON_DRIVER_TYPE == OracleDriverType.CX_ORACLE:
    logger.warning("cx_Oracle has a major new release under a new name python-oracledb: "
                   "https://oracle.github.io/python-oracledb/ \n"
                   "New projects should use python-oracledb instead of cx_Oracle\n"
                   "To use python-oracledb in thin mode set the environment variable ORA_PYTHON_DRIVER_TYPE=thin\n"
                   "For thick mode set ORA_PYTHON_DRIVER_TYPE=thick")
    import cx_Oracle as oracledb
elif ORA_PYTHON_DRIVER_TYPE == OracleDriverType.THICK:
    import oracledb
    oracledb.init_oracle_client()
elif ORA_PYTHON_DRIVER_TYPE == OracleDriverType.THIN:
    import oracledb
    SQLNET_ORA_CONFIG = OracleNetConfig.from_env()
else:
    raise dbt.exceptions.RuntimeException("Invalid value set for ORA_PYTHON_DRIVER_TYPE\n"
                                          "Use any one of 'cx', 'thin', or 'thick'")
