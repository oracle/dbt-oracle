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
from dataclasses import dataclass

from dbt.adapters.base.relation import BaseRelation, Policy



@dataclass
class OracleQuotePolicy(Policy):
    database: bool = False
    schema: bool = False
    identifier: bool = False


@dataclass
class OracleIncludePolicy(Policy):
    database: bool = False
    schema: bool = True
    identifier: bool = True


@dataclass(frozen=True, eq=False, repr=False)
class OracleRelation(BaseRelation):
    quote_policy: OracleQuotePolicy = OracleQuotePolicy()
    include_policy: OracleIncludePolicy = OracleIncludePolicy()

    def __post_init__(self):
        if self.database != self.schema and self.database:
            raise dbt.exceptions.RuntimeException(
                f'Cannot set database {self.database} in Oracle!'
            )

    @staticmethod
    def add_ephemeral_prefix(name):
        return f'dbt__cte__{name}__'

    def render(self):
        if self.include_policy.database and self.include_policy.schema:
            raise dbt.exceptions.RuntimeException(
                'Got a Oracle relation with schema and database set to '
                'include, but only one can be set'
            )
    return super().render()
