import pytest

from dbt.tests.adapter.basic.test_docs_generate import (BaseDocsGenReferences,
                                                        ref_models__schema_yml,
                                                        ref_models__ephemeral_copy_sql,
                                                        ref_models__docs_md)

from dbt.tests.adapter.basic.expected_catalog import no_stats

ref_sources__schema_yml = """
version: 2
sources:
  - name: my_source
    description: "{{ doc('source_info') }}"
    loader: a_loader
    schema: "{{ var('test_schema') }}"
    tables:
      - name: my_table
        description: "{{ doc('table_info') }}"
        identifier: seed
        quoting:
          identifier: true
        columns:
          - name: id
            description: "{{ doc('column_info') }}"
"""

ref_models__ephemeral_summary_sql = """
{{
  config(
    materialized = "table"
  )
}}

select "first_name", count(*) as ct from {{ref('ephemeral_copy')}}
group by "first_name"
order by "first_name" asc

"""

ref_models__view_summary_sql = """
{{
  config(
    materialized = "view"
  )
}}

select "first_name", ct from {{ref('ephemeral_summary')}}
order by ct asc

"""


class TextType:

    def __eq__(self, other):
        return other.upper().startswith('VARCHAR')


def expected_references_catalog(
    project,
    role,
    id_type,
    text_type,
    time_type,
    view_type,
    table_type,
    model_stats,
    bigint_type=None,
    seed_stats=None,
    case=None,
    case_columns=False,
    view_summary_stats=None,
):
    if case is None:

        def case(x):
            return x

    col_case = case if case_columns else lambda x: x

    if seed_stats is None:
        seed_stats = model_stats

    if view_summary_stats is None:
        view_summary_stats = model_stats

    model_database = project.database.upper()
    my_schema_name = project.test_schema.upper()

    summary_columns = {
        "first_name": {
            "name": "first_name",
            "index": 1,
            "type": TextType() ,
            "comment": None,
        },
        "CT": {
            "name": "CT",
            "index": 2,
            "type": bigint_type,
            "comment": None,
        },
    }

    seed_columns = {
        "id": {
            "name": col_case("id"),
            "index": 1,
            "type": id_type,
            "comment": None,
        },
        "first_name": {
            "name": col_case("first_name"),
            "index": 2,
            "type": TextType(),
            "comment": None,
        },
        "email": {
            "name": col_case("email"),
            "index": 3,
            "type": TextType(),
            "comment": None,
        },
        "ip_address": {
            "name": col_case("ip_address"),
            "index": 4,
            "type": TextType(),
            "comment": None,
        },
        "updated_at": {
            "name": col_case("updated_at"),
            "index": 5,
            "type": time_type,
            "comment": None,
        },
    }
    return {
        "nodes": {
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
                "columns": seed_columns,
            },
            "model.test.ephemeral_summary": {
                "unique_id": "model.test.ephemeral_summary",
                "metadata": {
                    "schema": my_schema_name,
                    "database": model_database,
                    "name": case("ephemeral_summary"),
                    "type": table_type,
                    "comment": None,
                    "owner": role,
                },
                "stats": model_stats,
                "columns": summary_columns,
            },
            "model.test.view_summary": {
                "unique_id": "model.test.view_summary",
                "metadata": {
                    "schema": my_schema_name,
                    "database": model_database,
                    "name": case("view_summary"),
                    "type": view_type,
                    "comment": None,
                    "owner": role,
                },
                "stats": view_summary_stats,
                "columns": summary_columns,
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
                "columns": seed_columns,
            },
        },
    }


class TestOracleDocsGenReferences(BaseDocsGenReferences):

    @pytest.fixture(scope="class")
    def models(self):
        return {
            "schema.yml": ref_models__schema_yml,
            "sources.yml": ref_sources__schema_yml,
            "view_summary.sql": ref_models__view_summary_sql,
            "ephemeral_summary.sql": ref_models__ephemeral_summary_sql,
            "ephemeral_copy.sql": ref_models__ephemeral_copy_sql,
            "docs.md": ref_models__docs_md,
        }

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
            "quoting": {"identifier": True},
        }

    @pytest.fixture(scope="class")
    def expected_catalog(self, project, profile_user):
        return expected_references_catalog(
            project,
            role=profile_user.upper(),
            id_type="NUMBER",
            text_type="VARCHAR2(16)",
            time_type="TIMESTAMP(6)",
            bigint_type="NUMBER",
            view_type="VIEW",
            table_type="BASE TABLE",
            model_stats=no_stats(),
            case_columns=False
        )
