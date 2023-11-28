def model(dbt, session):
    dbt.config(materialized="table")
    dbt.config(async_flag=True)
    dbt.config(timeout=1800)
    # oml.core.DataFrame referencing a dbt-sql model
    sales = session.sync(query="SELECT * FROM SH.SALES")
    return sales