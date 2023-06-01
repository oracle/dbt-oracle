def model(dbt, session):
    # Must be either table or incremental (view is not currently supported)
    dbt.config(materialized="table")
    # oml.core.DataFrame representing a datasource
    s_df = dbt.ref("sales_cost")
    return s_df
