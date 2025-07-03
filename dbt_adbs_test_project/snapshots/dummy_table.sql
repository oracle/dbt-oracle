
{% snapshot new_snapshot_dummy_table %}

  {{
      config(
         strategy = 'timestamp'
        , unique_key = 'id'
        , updated_at = 'created_at' 
        , hard_deletes = 'new_record'
      )
  }}

  SELECT * FROM {{ ref ('dummy_model') }}

{% endsnapshot %}
