import pytest

from dbt.tests.adapter.basic.test_docs_generate import (models__schema_yml,
                                                        models__readme_md,
                                                        models__model_sql,
                                                        BaseDocsGenerate)


from dbt.tests.adapter.basic.expected_catalog import no_stats
from dbt.tests.util import AnyInteger

models__second_model_sql = """
{{
    config(materialized='view')
}}

select * from {{ ref('seed') }}
"""


class TextType:

    def __eq__(self, other):
        return other.upper().startswith('VARCHAR')


def base_expected_catalog(
    project,
    role,
    id_type,
    text_type,
    time_type,
    view_type,
    table_type,
    model_stats,
    seed_stats=None,
    case=None,
    case_columns=False,
):

    if case is None:

        def case(x):
            return x

    col_case = case if case_columns else lambda x: x

    if seed_stats is None:
        seed_stats = model_stats

    model_database = case(project.database)
    my_schema_name = case(project.test_schema)
    alternate_schema = case(project.test_schema)

    expected_cols = {
        col_case("id"): {
            "name": col_case("id"),
            "index": AnyInteger(),
            "type": id_type,
            "comment": None,
        },
        col_case("first_name"): {
            "name": col_case("first_name"),
            "index": AnyInteger(),
            "type": TextType(),
            "comment": None,
        },
        col_case("email"): {
            "name": col_case("email"),
            "index": AnyInteger(),
            "type": TextType(),
            "comment": None,
        },
        col_case("ip_address"): {
            "name": col_case("ip_address"),
            "index": AnyInteger(),
            "type": TextType(),
            "comment": None,
        },
        col_case("updated_at"): {
            "name": col_case("updated_at"),
            "index": AnyInteger(),
            "type": time_type,
            "comment": None,
        },
    }

    return {
        "nodes": {
            "model.test.model": {
                "unique_id": "model.test.model",
                "metadata": {
                    "schema": my_schema_name,
                    "database": model_database,
                    "name": case("model"),
                    "type": view_type,
                    "comment": None,
                    "owner": role,
                },
                "stats": model_stats,
                "columns": expected_cols,
            },
            "model.test.second_model": {
                "unique_id": "model.test.second_model",
                "metadata": {
                    "schema": alternate_schema,
                    "database": project.database.upper(),
                    "name": case("second_model"),
                    "type": view_type,
                    "comment": None,
                    "owner": role,
                },
                "stats": model_stats,
                "columns": expected_cols,
            },
            "seed.test.seed": {
                "unique_id": "seed.test.seed",
                "metadata": {
                    "schema": my_schema_name,
                    "database": project.database.upper(),
                    "name": case("seed"),
                    "type": table_type,
                    "comment": None,
                    "owner": role,
                },
                "stats": seed_stats,
                "columns": expected_cols,
            },
        },
        "sources": {
            "source.test.my_source.my_table": {
                "unique_id": "source.test.my_source.my_table",
                "metadata": {
                    "schema": my_schema_name,
                    "database": project.database.upper(),
                    "name": case("seed"),
                    "type": table_type,
                    "comment": None,
                    "owner": role,
                },
                "stats": seed_stats,
                "columns": expected_cols,
            },
        },
    }


class TestOracleDocsGenerate(BaseDocsGenerate):

    @pytest.fixture(scope="class")
    def models(self):
        return {
            "schema.yml": models__schema_yml,
            "second_model.sql": models__second_model_sql,
            "readme.md": models__readme_md,
            "model.sql": models__model_sql,
        }

    @pytest.fixture(scope="class")
    def expected_catalog(self, project, profile_user):
        return base_expected_catalog(
            project,
            role=profile_user.upper(),
            id_type="NUMBER",
            text_type="VARCHAR2(16)",
            time_type="TIMESTAMP(6)",
            view_type="VIEW",
            table_type="BASE TABLE",
            model_stats=no_stats(),
            case=lambda x: x.upper(),
            case_columns=False
        )

    @pytest.fixture(scope="class")
    def project_config_update(self, unique_schema):
        alternate_schema = unique_schema
        return {
            "asset-paths": ["assets", "invalid-asset-paths"],
            "vars": {
                "test_schema": unique_schema,
                "alternate_schema": alternate_schema,
            },
            "seeds": {
                "quote_columns": True,
            },
            "quoting": {"identifier": False},
        }
