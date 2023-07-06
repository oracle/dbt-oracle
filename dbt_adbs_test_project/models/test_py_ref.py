def model(dbt, session):
    # Must be either table or incremental (view is not currently supported)
    dbt.config(materialized="table")
    dbt.config(async_flag=True)
    dbt.config(timeout=900)  # In seconds
    dbt.config(service="HIGH")  # LOW, MEDIUM, HIGH
    # oml.core.DataFrame representing a datasource
    s_df = dbt.ref("sales_cost")
    return s_df
