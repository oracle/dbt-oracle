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
from typing import Optional, Set

import agate
from dbt.adapters.oracle.relation_configs.base import OracleRelationConfigBase
from dbt.adapters.relation_configs import RelationResults, RelationConfigChange

from dbt.contracts.relation import ComponentName

from dbt.contracts.graph.nodes import ModelNode
from dbt.exceptions import DbtRuntimeError
from dbt.events import AdapterLogger

logger = AdapterLogger("oracle")

@dataclass(frozen=True, eq=True, unsafe_hash=True)
class OracleMaterializedViewConfig(OracleRelationConfigBase):
    """
    mview_name: Name of the materialized view

    query: Query that defines the materialized view

    refresh_mode: Refresh mode of the materialized view
        DEMAND - Oracle Database refreshes this materialized view whenever an appropriate refresh procedure is called
        COMMIT - Oracle Database refreshes this materialized view when a transaction on one of the materialized view's masters commits
        NEVER - Oracle Database never refreshes this materialized view

    refresh_method: Default method used to refresh the materialized view (can be overridden through the API)
        COMPLETE (C) - Materialized view is completely refreshed from the masters
        FORCE (?) - Oracle Database performs a fast refresh if possible, otherwise a complete refresh
        FAST (F) - Oracle Database performs an incremental refresh applying changes that correspond to changes in the masters since the last refresh
        NEVER (N) - User specified that the Oracle Database should not refresh this materialized view

    build_mode: Indicates how the materialized view was populated during creation
        IMMEDIATE - Populated from the masters during creation
        DEFERRED - Not populated during creation. Must be explicitly populated later by the user.
        PREBUILT - Populated with an existing table during creation. The relationship of the contents of this prebuilt table to the materialized view's masters is unknown to the Oracle Database.

    rewrite_enabled: Indicates whether rewrite is enabled (Y) or not (N)

    """
    mview_name: str
    query: str
    refresh_mode: Optional[str] = "demand"
    refresh_method: Optional[str] = "force"
    build_mode: Optional[str] = "immediate"
    query_rewrite: Optional[str] = "disable"

    @classmethod
    def from_dict(cls, config_dict) -> "OracleMaterializedViewConfig":
        kwargs_dict = {
            "mview_name": cls._render_part(ComponentName.Identifier, config_dict.get("mview_name")),
            "query": config_dict.get("query"),
            "refresh_mode": config_dict.get("refresh_mode"),
            "refresh_method": config_dict.get("refresh_method"),
            "build_mode": config_dict.get("build_mode"),
            "query_rewrite": config_dict.get("query_rewrite")
        }

        materialized_view: "OracleMaterializedViewConfig" = super().from_dict(kwargs_dict)  # type: ignore
        return materialized_view

    @classmethod
    def from_model_node(cls, model_node: ModelNode) -> "OracleMaterializedViewConfig":
        materialized_view_config = cls.parse_model_node(model_node)
        materialized_view = cls.from_dict(materialized_view_config)
        return materialized_view

    @classmethod
    def parse_model_node(cls, model_node: ModelNode) -> dict:
        config_dict = {
            "mview_name": model_node.identifier,
            "refresh_mode": model_node.config.get("refresh_mode", "demand"),
            "refresh_method": model_node.config.get("refresh_method", "force"),
            "build_mode": model_node.config.get("build_mode", "immediate"),
            "query_rewrite": model_node.config.get("query_rewrite", "disable")
        }
        if query := model_node.compiled_code:
            config_dict.update({"query": query.strip()})

        return config_dict

    @classmethod
    def from_relation_results(cls, relation_results: RelationResults) -> "OracleMaterializedViewConfig":
        materialized_view_config = cls.parse_relation_results(relation_results)
        materialized_view = cls.from_dict(materialized_view_config)
        return materialized_view

    @classmethod
    def parse_relation_results(cls, relation_results: RelationResults) -> dict:
        """
        Translate agate objects from the database into a standard dictionary.
        """

        materialized_view: agate.Row = cls._get_first_row(relation_results.get("materialized_view"))
        logger.debug(f"Materialized View data is {materialized_view}")
        config_dict = {
            "mview_name": materialized_view.get("mview_name".upper()),
            "refresh_mode": materialized_view.get("refresh_mode".upper()),
            "refresh_method": materialized_view.get("refresh_method".upper()),
            "build_mode": materialized_view.get("build_mode".upper()),
            "query": materialized_view.get("query".upper()),
        }
        logger.debug(f"Materialized View config is {config_dict}")
        if materialized_view.get('rewrite_enabled'.upper()).upper() == 'Y':
            config_dict["query_rewrite"] = "enable"
        else:
            config_dict["query_rewrite"] = "disable"

        return config_dict


@dataclass(frozen=True, eq=True, unsafe_hash=True)
class OracleRefreshModeConfigChange(RelationConfigChange):
    context: Optional[str] = None

    @property
    def requires_full_refresh(self) -> bool:
        return False


@dataclass(frozen=True, eq=True, unsafe_hash=True)
class OracleRefreshMethodConfigChange(RelationConfigChange):
    context: Optional[str] = None

    @property
    def requires_full_refresh(self) -> bool:
        return True

@dataclass(frozen=True, eq=True, unsafe_hash=True)
class OracleBuildModeConfigChange(RelationConfigChange):
    context: Optional[str] = None

    @property
    def requires_full_refresh(self) -> bool:
        return False

@dataclass(frozen=True, eq=True, unsafe_hash=True)
class OracleQueryRewriteConfigChange(RelationConfigChange):
    context: Optional[str] = None

    @property
    def requires_full_refresh(self) -> bool:
        return False

@dataclass(frozen=True, eq=True, unsafe_hash=True)
class OracleQueryConfigChange(RelationConfigChange):
    context: Optional[str] = None

    @property
    def requires_full_refresh(self) -> bool:
        return True


@dataclass
class OracleMaterializedViewConfigChangeset:
    refresh_mode: Optional[OracleRefreshMethodConfigChange] = None
    refresh_method: Optional[OracleRefreshMethodConfigChange] = None
    build_mode: Optional[OracleBuildModeConfigChange] = None
    query_rewrite: Optional[OracleQueryRewriteConfigChange] = None
    query: Optional[OracleQueryConfigChange] = None

    @property
    def requires_full_refresh(self) -> bool:
        return any(
            {
                self.refresh_mode.requires_full_refresh if self.refresh_mode else False,
                self.refresh_method.requires_full_refresh if self.refresh_method else False,
                self.build_mode.requires_full_refresh if self.build_mode else False,
                self.query_rewrite.requires_full_refresh if self.query_rewrite else False,
                self.query.requires_full_refresh if self.query else False
            }
        )

    @property
    def has_changes(self) -> bool:
        return any(
            {
                self.refresh_mode if self.refresh_mode else False,
                self.refresh_method if self.refresh_method else False,
                self.build_mode if self.build_mode else False,
                self.query_rewrite if self.query_rewrite else False,
                self.query if self.query else False
            }
        )
