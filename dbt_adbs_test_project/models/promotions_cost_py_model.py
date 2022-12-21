def model(dbt, session):
    # Must be either table or incremental (view is not currently supported)
    dbt.config(materialized="table")

    # oml.core.DataFrame referencing a dbt-sql model
    promotion_cost = dbt.ref("direct_sales_channel_promo_cost")
    return promotion_cost
