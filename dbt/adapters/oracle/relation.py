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
from typing import Optional

from dataclasses import dataclass, field

from dbt.adapters.base.relation import BaseRelation
from dbt.adapters.relation_configs import (
    RelationConfigBase,
    RelationConfigChangeAction,
    RelationResults,
)
from dbt.context.providers import RuntimeConfigObject
from dbt.contracts.graph.nodes import ModelNode
from dbt.contracts.relation import RelationType
from dbt.exceptions import DbtRuntimeError

from dbt.adapters.oracle.relation_configs import (
    OracleMaterializedViewConfig,
    OracleRefreshMethodConfigChange,
    OracleMaterializedViewConfigChangeset,
    OracleRefreshModeConfigChange,
    OracleBuildModeConfigChange,
    OracleQueryRewriteConfigChange,
    OracleQueryConfigChange,
    OracleQuotePolicy,
    OracleIncludePolicy)

from dbt.events import AdapterLogger

logger = AdapterLogger("oracle")


@dataclass(frozen=True, eq=False, repr=False)
class OracleRelation(BaseRelation):
    quote_policy: OracleQuotePolicy = field(default_factory=lambda: OracleQuotePolicy())
    include_policy: OracleIncludePolicy = field(default_factory=lambda: OracleIncludePolicy())
    relation_configs = {
        RelationType.MaterializedView.value: OracleMaterializedViewConfig
    }

    @staticmethod
    def add_ephemeral_prefix(name):
        return f'dbt__cte__{name}__'

    @classmethod
    def from_runtime_config(cls, runtime_config: RuntimeConfigObject) -> RelationConfigBase:
        model_node: ModelNode = runtime_config.model
        relation_type: str = model_node.config.materialized

        if relation_config := cls.relation_configs.get(relation_type):
            return relation_config.from_model_node(model_node)

        raise DbtRuntimeError(
            f"from_runtime_config() is not supported for the provided relation type: {relation_type}"
        )

    @classmethod
    def materialized_view_config_changeset(
            cls, relation_results: RelationResults,
            runtime_config: RuntimeConfigObject) -> Optional[OracleMaterializedViewConfigChangeset]:
        config_change_collection = OracleMaterializedViewConfigChangeset()

        existing_materialized_view = OracleMaterializedViewConfig.from_relation_results(
            relation_results
        )
        new_materialized_view = OracleMaterializedViewConfig.from_model_node(
            runtime_config.model
        )

        assert isinstance(existing_materialized_view, OracleMaterializedViewConfig)
        assert isinstance(new_materialized_view, OracleMaterializedViewConfig)

        if new_materialized_view.refresh_method.upper() != existing_materialized_view.refresh_method.upper():
            config_change_collection.refresh_method = OracleRefreshMethodConfigChange(
                action=RelationConfigChangeAction.alter,
                context=new_materialized_view.refresh_method
            )

        if new_materialized_view.refresh_mode.upper() != existing_materialized_view.refresh_mode.upper():
            config_change_collection.refresh_mode = OracleRefreshModeConfigChange(
                action=RelationConfigChangeAction.alter,
                context=new_materialized_view.refresh_mode
            )

        if new_materialized_view.build_mode.upper() != existing_materialized_view.build_mode.upper():
            config_change_collection.build_mode = OracleBuildModeConfigChange(
                action=RelationConfigChangeAction.alter,
                context=new_materialized_view.build_mode
            )

        if new_materialized_view.query_rewrite.upper() != existing_materialized_view.query_rewrite.upper():
            config_change_collection.query_rewrite = OracleQueryRewriteConfigChange(
                action=RelationConfigChangeAction.alter,
                context=new_materialized_view.query_rewrite
            )

        if new_materialized_view.query.upper() != existing_materialized_view.query.upper():
            config_change_collection.query = OracleQueryConfigChange(
                action=RelationConfigChangeAction.create,
                context=new_materialized_view.query
            )

        logger.debug(f"Config change collection {config_change_collection}")

        if config_change_collection.has_changes:

            if config_change_collection.refresh_mode is None:
                config_change_collection.refresh_mode = OracleRefreshModeConfigChange(
                    action=RelationConfigChangeAction.alter,
                    context=existing_materialized_view.refresh_mode)

            if config_change_collection.query_rewrite is None:
                config_change_collection.query_rewrite = OracleQueryRewriteConfigChange(
                    action=RelationConfigChangeAction.alter,
                    context=existing_materialized_view.query_rewrite)

            if config_change_collection.refresh_method is None:
                config_change_collection.refresh_method = OracleRefreshMethodConfigChange(
                    action=RelationConfigChangeAction.alter,
                    context=existing_materialized_view.refresh_method)

            if config_change_collection.build_mode is None:
                config_change_collection.build_mode = OracleBuildModeConfigChange(
                    action=RelationConfigChangeAction.alter,
                    context=existing_materialized_view.build_mode)

            if config_change_collection.query is None:
                config_change_collection.query = OracleQueryConfigChange(
                    action=RelationConfigChangeAction.create,
                    context=existing_materialized_view.query)

            return config_change_collection

        return None
