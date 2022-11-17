{% snapshot customer_details %}
    {{        config(
                strategy='timestamp',
                unique_key='cust_id',
                updated_at='updated_at',
                invalidate_hard_deletes=True
            )
    }}
    select * from dbt_customers
{% endsnapshot %}