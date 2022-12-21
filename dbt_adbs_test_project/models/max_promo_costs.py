def model(dbt, session):
    # Must be either table or incremental (view is not currently supported)
    dbt.config(materialized="table")

    # oml.core.DataFrame referencing a dbt-py model
    promotion_cost = dbt.ref("promotions_cost_py_model")

    # execute SQL
    cr = session.cursor()
    _ = cr.execute("SELECT MAX(promo_cost) FROM promotions_cost_py_model")
    max_promo_cost = cr.fetchone()[0]

    # oml.core.DataFrame filter all sales channel promotions with max cost
    max_promo_costs = promotion_cost[promotion_cost["PROMO_COST"] == max_promo_cost]

    # Compute the promotion cost to benefits ratio
    cost_to_benefits_ratio = max_promo_costs["PROMO_COST"]/(max_promo_costs["AMOUNT_SOLD"])

    # Concat a new column "COST_TO_AMOUNT_SOLD_RATIO" rounded to 3 decimal places
    max_promo_costs = max_promo_costs.concat({"COST_TO_AMOUNT_SOLD_RATIO": cost_to_benefits_ratio.round(3)})

    return max_promo_costs
