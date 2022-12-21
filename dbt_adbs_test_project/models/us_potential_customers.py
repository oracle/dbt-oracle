def model(dbt, session):
    dbt.config(materialized="table")

    sql = f"""SELECT customer.cust_first_name,
       customer.cust_last_name,
       customer.cust_gender,
       customer.cust_marital_status,
       customer.cust_street_address,
       customer.cust_email,
       customer.cust_credit_limit,
       customer.cust_income_level
    FROM sh.customers customer, sh.countries country
    WHERE country.country_iso_code = ''US''
    AND customer.country_id = country.country_id"""

    # session.sync(query) will run the sql query and returns a oml.core.DataFrame
    us_potential_customers = session.sync(query=sql)

    # Compute an ad-hoc anomaly score on the credit limit
    median_credit_limit = us_potential_customers["CUST_CREDIT_LIMIT"].median()
    mean_credit_limit = us_potential_customers["CUST_CREDIT_LIMIT"].mean()
    anomaly_score = (us_potential_customers["CUST_CREDIT_LIMIT"] - median_credit_limit)/(median_credit_limit - mean_credit_limit)

    # Add a new column "CUST_CREDIT_ANOMALY_SCORE"
    us_potential_customers = us_potential_customers.concat({"CUST_CREDIT_ANOMALY_SCORE": anomaly_score.round(3)})

    # Return potential customers dataset as a oml.core.DataFrame
    return us_potential_customers
