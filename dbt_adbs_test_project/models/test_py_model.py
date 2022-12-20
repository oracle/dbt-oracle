def model(dbt, session):
       # Must be either table or incremental (view is not currently supported)
       dbt.config(materialized="table")
       # Dataframe representing a source
       s_df = dbt.source("sh_database", "countries")
       # DataFrame representing an upstream model
       df = dbt.ref("seed")
       return df.pull()