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

import pytest

# dbt imports
from dbt.clients.yaml_helper import load_yaml_text
import dbt.config
from dbt.context.base import generate_base_context

# dbt-oracle imports
from dbt.adapters.oracle import OracleAdapterCredentials
from dbt.adapters.oracle.connections import OracleConnectionMethod


def get_credentials(profile_yml):
    "Render a YAML string profiles.yml into credentials"
    dicty_thing = load_yaml_text(profile_yml)
    renderer = dbt.config.renderer.ProfileRenderer(generate_base_context({}))
    profile = dbt.config.Profile.from_raw_profiles(
        dicty_thing, 'default', renderer
    )
    return profile.credentials


# Define data
SCENARIOS = {
    "host": {
        "method": OracleConnectionMethod.HOST,
        "profile": """
            default:
                target: target
                outputs:
                    target:
                        type: oracle
                        host: localhost
                        user: dbt_test
                        pass: dbt_test
                        protocol: tcps
                        service: xe
                        schema: dbt_test
                        port: 1522
                        threads: 1
            """,
                    "dsn": "tcps://localhost:1522/xe",
                },
    "host_service": {
        "method": OracleConnectionMethod.HOST,
        "profile": """
            default:
                target: target
                outputs:
                    target:
                        type: oracle
                        host: localhost
                        user: dbt_test
                        pass: dbt_test
                        service: xe_ha.host.tld
                        schema: dbt_test
                        protocol: tcps
                        port: 1522
                        threads: 1
            """,
        "dsn": "tcps://localhost:1522/xe_ha.host.tld",
    },
    "tns": {
        "method": OracleConnectionMethod.TNS,
        "profile": """
            default:
                target: target
                outputs:
                    target:
                        type: oracle
                        user: dbt_test
                        pass: dbt_test
                        tns_name: xe
                        schema: dbt_test
                        port: 1522
                        protocol: tcps
                        threads: 1
            """,
        "dsn": "xe",
    },
    "connection_string": {
        "method": OracleConnectionMethod.CONNECTION_STRING,
        "profile": """
            default:
                target: target
                outputs:
                    target:
                        type: oracle
                        host: localhost
                        user: dbt_test
                        pass: dbt_test
                        connection_string: "(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=localhost)(PORT=1522))(CONNECT_DATA=(SERVICE_NAME=xe)))"
                        schema: dbt_test
                        port: 1522
                        threads: 1
            """,
        "dsn": "(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=localhost)(PORT=1522))(CONNECT_DATA=(SERVICE_NAME=xe)))",
    },
}


@pytest.fixture(scope="module", params=SCENARIOS.keys())
def scenario(request):
    return SCENARIOS[request.param]


def test_oracle_credentials(scenario):
    for method, parameters in SCENARIOS.items():
        credentials = get_credentials(scenario["profile"])
        assert credentials.connection_method() == scenario["method"]
        assert credentials.get_dsn() == scenario["dsn"]
