"""
Copyright (c) 2023, Oracle and/or its affiliates.

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
from typing import Any, Dict, Optional

import agate
from dbt.adapters.base.relation import Policy
from dbt.adapters.relation_configs import (
    RelationConfigBase,
    RelationResults,
)
from dbt.contracts.graph.nodes import ModelNode
from dbt.contracts.relation import ComponentName

from dbt.adapters.oracle.relation_configs.policies import (
    OracleQuotePolicy,
    OracleIncludePolicy,
)


@dataclass(frozen=True, eq=True, unsafe_hash=True)
class OracleRelationConfigBase(RelationConfigBase):
    """
    This base class implements a few boilerplate methods and provides some light structure for Oracle relations.
    """

    @classmethod
    def include_policy(cls) -> Policy:
        return OracleIncludePolicy()

    @classmethod
    def quote_policy(cls) -> Policy:
        return OracleQuotePolicy()

    @classmethod
    def from_model_node(cls, model_node: ModelNode):
        relation_config = cls.parse_model_node(model_node)
        relation = cls.from_dict(relation_config)
        return relation

    @classmethod
    def parse_model_node(cls, model_node: ModelNode) -> Dict[str, Any]:
        raise NotImplementedError(
            "`parse_model_node()` needs to be implemented on this RelationConfigBase instance"
        )

    @classmethod
    def from_relation_results(cls, relation_results: RelationResults):
        relation_config = cls.parse_relation_results(relation_results)
        relation = cls.from_dict(relation_config)
        return relation

    @classmethod
    def parse_relation_results(cls, relation_results: RelationResults) -> Dict[str, Any]:
        raise NotImplementedError(
            "`parse_relation_results()` needs to be implemented on this RelationConfigBase instance"
        )

    @classmethod
    def _render_part(cls, component: ComponentName, value: Optional[str]) -> Optional[str]:
        if cls.include_policy().get_part(component) and value:
            if cls.quote_policy().get_part(component):
                return f'"{value}"'
            return value.lower()
        return None

    @classmethod
    def _get_first_row(cls, results: agate.Table) -> agate.Row:
        try:
            return results.rows[0]
        except IndexError:
            return agate.Row(values=set())
