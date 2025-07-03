{% snapshot snapshot_label_table %}

  {{
      config(
         strategy = 'timestamp'
        , unique_key = 'id'
        , updated_at = 'created_at'
        , hard_deletes = 'new_record'
      )
  }}

  SELECT * FROM {{ ref ('label_data') }}

{% endsnapshot %}

