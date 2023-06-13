def model(dbt, session):
    # Must be either table or incremental
    dbt.config(materialized="incremental", incremental_strategy="merge")
    # oml.DataFrame representing a datasource
    sales_cost_df = dbt.ref("sales_cost")

    if dbt.is_incremental:
        cr = session.cursor()
        result = cr.execute(f"select max(cost_timestamp) from {dbt.this.identifier}")
        max_timestamp = result.fetchone()[0]
        sales_cost_df = sales_cost_df[sales_cost_df["COST_TIMESTAMP"] > max_timestamp]

    return sales_cost_df
