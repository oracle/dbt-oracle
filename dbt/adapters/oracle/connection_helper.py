import enum
import os

import dbt.exceptions
from dbt.events import AdapterLogger

logger = AdapterLogger("oracle")


class OracleNetConfig(dict):
    """The sqlnet.ora file is only supported in the python-oracledb Thick mode.
    In Thin mode, the user can pass these as environment variables

      - ssl_server_cert_dn: the distinguished name (DN) which should be
        matched with the server. This value is ignored if the
        ssl_server_dn_match parameter is not set to the value True.

      - ssl_server_dn_match: boolean indicating whether the server
        certificate distinguished name (DN) should be matched in addition to
        the regular certificate verification that is performed.

      - wallet_password: the password to use to decrypt the wallet, if it is
        encrypted. This value is only used in thin mode (default: None)

      - wallet_location: the directory where the wallet can be found. In thin
        mode this must be the directory containing the PEM-encoded wallet
        file ewallet.pem. In thick mode this must be the directory containing
        the file cwallet.sso (default: None)

      - expire_time: an integer indicating the number of minutes between the
        sending of keepalive probes. If this parameter is set to a value
        greater than zero it enables keepalive (default: 0)

      - retry_count: the number of times that a connection attempt should be
        retried before the attempt is terminated (default: 0)

      - retry_delay: the number of seconds to wait before making a new
        connection attempt (default: 0)

      - tcp_connect_timeout: a float indicating the maximum number of seconds
        to wait for establishing a connection to the database host (default:
        60.0)

      - config_dir: directory in which the optional tnsnames.ora
        configuration file is located. This value is only used in thin mode.
        For thick mode use the config_dir parameter of init_oracle_client()

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
        'config_dir',
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
    logger.info("Running in cx mode")
    import cx_Oracle as oracledb
elif ORA_PYTHON_DRIVER_TYPE == OracleDriverType.THICK:
    import oracledb
    logger.info("Running in thick mode")
    oracledb.init_oracle_client()
elif ORA_PYTHON_DRIVER_TYPE == OracleDriverType.THIN:
    import oracledb
    SQLNET_ORA_CONFIG = OracleNetConfig.from_env()
    logger.info("Running in thin mode")
else:
    raise dbt.exceptions.RuntimeException("Invalid value set for ORA_PYTHON_DRIVER_TYPE\n"
                                          "Use any one of 'cx', 'thin', or 'thick'")
