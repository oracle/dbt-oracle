def model(dbt, session):
    # Must be either table or incremental (view is not currently supported)
    dbt.config(materialized="table")
    # dbt.config(conda_env_name="dbt_py_env")
    # oml.core.DataFrame representing a datasource
    s_df = dbt.source("sh_database", "channels")
    return s_df
