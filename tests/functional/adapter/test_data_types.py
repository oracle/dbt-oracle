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

from dbt.tests.adapter.utils.data_types.test_type_boolean import BaseTypeBoolean
from dbt.tests.adapter.utils.data_types.test_type_bigint import BaseTypeBigInt
from dbt.tests.adapter.utils.data_types.test_type_float import BaseTypeFloat
from dbt.tests.adapter.utils.data_types.test_type_int import BaseTypeInt
from dbt.tests.adapter.utils.data_types.test_type_numeric import BaseTypeNumeric


models__bigint_expected_sql = """
select 9223372036854775800 as bigint_col from dual
""".lstrip()

models__bigint_actual_sql = """
select cast('9223372036854775800' as {{ type_bigint() }}) as bigint_col from dual
"""

models__float_actual_sql = """
select cast('1.2345' as {{ type_float() }}) as float_col from dual
"""

models__int_actual_sql = """
select cast('12345678' as {{ type_int() }}) as int_col from dual
"""

models__numeric_actual_sql = """
select cast('1.2345' as {{ type_numeric() }}) as numeric_col from dual
"""


seeds__boolean_expected_csv = """boolean_col
1
""".lstrip()

models__boolean_actual_sql = """
select cast('1' as {{ type_boolean() }}) as boolean_col from dual
"""


class TestTypeBigIntOracle(BaseTypeBigInt):

    @pytest.fixture(scope="class")
    def models(self):
        return {
            "expected.sql": models__bigint_expected_sql,
            "actual.sql": self.interpolate_macro_namespace(models__bigint_actual_sql, "type_bigint"),
        }


class TestTypeFloatOracle(BaseTypeFloat):

    @pytest.fixture(scope="class")
    def models(self):
        return {"actual.sql": self.interpolate_macro_namespace(models__float_actual_sql, "type_float")}


class TestTypeIntOracle(BaseTypeInt):

    @pytest.fixture(scope="class")
    def models(self):
        return {"actual.sql": self.interpolate_macro_namespace(models__int_actual_sql, "type_int")}


class TestTypeNumericOracle(BaseTypeNumeric):

    @pytest.fixture(scope="class")
    def models(self):
        return {"actual.sql": self.interpolate_macro_namespace(models__numeric_actual_sql, "type_numeric")}


class TestTypeBooleanOracle(BaseTypeBoolean):

    @pytest.fixture(scope="class")
    def seeds(self):
        return {"expected.csv": seeds__boolean_expected_csv}

    @pytest.fixture(scope="class")
    def models(self):
        return {"actual.sql": self.interpolate_macro_namespace(models__boolean_actual_sql, "type_boolean")}

