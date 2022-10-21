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

from dbt.tests.adapter.utils.test_concat import BaseConcat
from dbt.tests.adapter.utils.test_intersect import BaseIntersect
from dbt.tests.adapter.utils.test_escape_single_quotes import BaseEscapeSingleQuotesQuote
from dbt.tests.adapter.utils.test_except import BaseExcept
from dbt.tests.adapter.utils.test_hash import BaseHash
from dbt.tests.adapter.utils.test_string_literal import BaseStringLiteral
from dbt.tests.adapter.utils.test_position import BasePosition
from dbt.tests.adapter.utils.test_right import BaseRight
from dbt.tests.adapter.utils.test_cast_bool_to_text import BaseCastBoolToText
from dbt.tests.adapter.utils.test_replace import BaseReplace
from dbt.tests.adapter.utils.test_length import BaseLength
from dbt.tests.adapter.utils.test_current_timestamp import BaseCurrentTimestampNaive

from dbt.tests.adapter.utils.fixture_cast_bool_to_text import models__test_cast_bool_to_text_yml
from dbt.tests.adapter.utils.fixture_escape_single_quotes import models__test_escape_single_quotes_yml
from dbt.tests.adapter.utils.fixture_string_literal import models__test_string_literal_yml
from dbt.tests.adapter.utils.fixture_replace import models__test_replace_yml


# Oracle requires FROM DUAL
models__test_escape_single_quotes_quote_sql = """
select '{{ escape_single_quotes("they're") }}' as actual, 'they''re' as expected from dual union all
select '{{ escape_single_quotes("they are") }}' as actual, 'they are' as expected from dual
"""

models__test_string_literal_sql = """
select {{ string_literal("abc") }} as actual, 'abc' as expected from dual union all
select {{ string_literal("1") }} as actual, '1' as expected from dual union all
select {{ string_literal("") }} as actual, '' as expected from dual union all
select {{ string_literal(none) }} as actual, 'None' as expected from dual
"""

# Oracle returns upper-case encoded MD5 hash
seeds__data_hash_csv = """input_1,output
ab,187EF4436122D1CC2F40DC2B92F0EBA0
a,0CC175B9C0F1B6A831C399E269772661
1,C4CA4238A0B923820DCC509A6F75849B
,D41D8CD98F00B204E9800998ECF8427E
"""

models__test_cast_bool_to_text_sql = """
with data as (

    select 0 as input, 'false' as expected from dual union all 
    select 1 as input, 'true' as expected from dual union all
    select null as input, null as expected from dual

)
select
    {{ cast_bool_to_text("input=1") }} actual,
    expected
from data
"""

models__test_replace_sql = """
with data as (

    select

        string_text,
        coalesce(search_chars, '') as old_chars,
        coalesce(replace_chars, '') as new_chars,
        result

    from {{ ref('data_replace') }}

)

select

    {{ replace('string_text', 'old_chars', 'new_chars') }} as actual,
    result as expected

from data
"""

models__current_ts_sql = """
select {{ dbt.current_timestamp() }} as current_ts_column from dual
"""


class TestCastBoolToText(BaseCastBoolToText):

    @pytest.fixture(scope="class")
    def models(self):
        return {
            "test_cast_bool_to_text.yml": models__test_cast_bool_to_text_yml,
            "test_cast_bool_to_text.sql": self.interpolate_macro_namespace(
                models__test_cast_bool_to_text_sql, "cast_bool_to_text"
            ),
        }


class TestIntersect(BaseIntersect):
    pass


class TestConcat(BaseConcat):
    pass


class TestEscapeSingleQuotesQuote(BaseEscapeSingleQuotesQuote):

    @pytest.fixture(scope="class")
    def models(self):
        return {
            "test_escape_single_quotes.yml": models__test_escape_single_quotes_yml,
            "test_escape_single_quotes.sql": self.interpolate_macro_namespace(
                models__test_escape_single_quotes_quote_sql, "escape_single_quotes"
            ),
        }


class TestExcept(BaseExcept):
    pass


class TestHash(BaseHash):

    @pytest.fixture(scope="class")
    def seeds(self):
        return {"data_hash.csv": seeds__data_hash_csv}


class TestStringLiteral(BaseStringLiteral):

    @pytest.fixture(scope="class")
    def models(self):
        return {
            "test_string_literal.yml": models__test_string_literal_yml,
            "test_string_literal.sql": self.interpolate_macro_namespace(
                models__test_string_literal_sql, "string_literal"
            ),
        }


class TestStringPosition(BasePosition):
    pass


class TestStringRight(BaseRight):
    pass


class TestStringReplace(BaseReplace):

    @pytest.fixture(scope="class")
    def models(self):
        return {
            "test_replace.yml": models__test_replace_yml,
            "test_replace.sql": self.interpolate_macro_namespace(
                models__test_replace_sql, "replace"
            ),
        }


class TestStringLength(BaseLength):
    pass


class TestCurrentTimestampNaiveOracle(BaseCurrentTimestampNaive):

    @pytest.fixture(scope="class")
    def models(self):
        return {
            "current_ts.sql": models__current_ts_sql,
        }

