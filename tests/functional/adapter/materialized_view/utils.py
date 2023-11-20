from typing import List, Optional

from dbt.adapters.base.relation import BaseRelation
from dbt.adapters.oracle.relation import OracleRelation


def query_relation_type(project, relation: BaseRelation) -> Optional[str]:
    assert isinstance(relation, OracleRelation)

    sql = f"""
        with tables as
      (select SYS_CONTEXT('userenv', 'DB_NAME') table_catalog,
         owner table_schema,
         table_name,
         case
           when iot_type = 'Y'
           then 'IOT'
           when temporary = 'Y'
           then 'TEMP'
           else 'BASE TABLE'
         end table_type
       from sys.all_tables
       where upper(table_name) not in (select upper(mview_name) from sys.all_mviews)
       union all
       select SYS_CONTEXT('userenv', 'DB_NAME'),
         owner,
         view_name,
         'VIEW'
       from sys.all_views
       union all
       select SYS_CONTEXT('userenv', 'DB_NAME'),
        owner,
        mview_name,
        'MATERIALIZED VIEW'
        from sys.all_mviews
  )
  select case table_type
      when 'BASE TABLE' then 'table'
      when 'VIEW' then 'view'
      when 'MATERIALIZED VIEW' then 'materialized_view'
    end as "relation_type"
  from tables
  where table_type in ('BASE TABLE', 'VIEW', 'MATERIALIZED VIEW')
    and upper(table_schema) = upper('{relation.schema}')
    and upper(table_name) = upper('{relation.identifier}') 
    """

    results = project.run_sql(sql, fetch="all")
    if len(results) == 0:
        return None
    elif len(results) > 1:
        raise ValueError(f"More than one instance of {relation.identifier} found!")
    else:
        return results[0][0]


def query_refresh_method(project, relation: OracleRelation):
    sql = f"""SELECT refresh_method
              FROM sys.all_mviews
              WHERE mview_name = '{ relation.identifier.upper() }'"""
    return project.run_sql(sql, fetch="one")[0].upper()


def query_refresh_mode(project, relation: OracleRelation):
    sql = f"""SELECT refresh_mode
              FROM sys.all_mviews
              WHERE mview_name = '{ relation.identifier.upper() }'"""
    return project.run_sql(sql, fetch="one")[0].upper()


def query_build_mode(project, relation: OracleRelation):
    sql = f"""SELECT build_mode
              FROM sys.all_mviews
              WHERE mview_name = '{relation.identifier.upper()}'"""
    return project.run_sql(sql, fetch="one")[0].upper()


def query_rewrite_enabled(project, relation: OracleRelation):
    sql = f"""SELECT rewrite_enabled
              FROM sys.all_mviews
              WHERE mview_name = '{relation.identifier.upper() }'"""
    return "enable" if project.run_sql(sql, fetch="one")[0] == "Y" else "disable"

