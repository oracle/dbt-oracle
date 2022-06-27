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
import os

# Import the functional fixtures as a plugin
# Note: fixtures with session scope need to be local

pytest_plugins = ["dbt.tests.fixtures.project"]


# The profile dictionary, used to write out profiles.yml
@pytest.fixture(scope="class")
def dbt_profile_target():
    return {
        'type': 'oracle',
        'threads': 4,
        'user': os.getenv('DBT_ORACLE_USER'),
        'pass': os.getenv('DBT_ORACLE_PASSWORD'),
        'host': os.getenv('DBT_ORACLE_HOST'),
        'schema': os.getenv('DBT_ORACLE_SCHEMA'),
        'database': os.getenv('DBT_ORACLE_DATABASE'),
        'service': os.getenv('DBT_ORACLE_SERVICE'),
        'protocol': os.getenv('DBT_ORACLE_PROTOCOL'),
        'port': os.getenv('DBT_ORACLE_PORT')
    }


@pytest.fixture(scope="class")
def unique_schema(request, prefix) -> str:
    return os.getenv('DBT_ORACLE_SCHEMA')
