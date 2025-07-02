{#
 Copyright (c) 2022, Oracle and/or its affiliates.

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

     https://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
#}
{% snapshot promotion_costs_snapshot %}
    {{        config(
                strategy='check',
                unique_key='promo_id',
                check_cols='all',
                hard_deletes='invalidate',
                snapshot_meta_column_names={
                    "dbt_valid_from": "promo_valid_from",
                    "dbt_valid_to": "promo_valid_to",
                    "dbt_scd_id": "dbt_scd_id"
                }
            )
    }}
    select * from {{ ref('promotion_costs') }}
{% endsnapshot %}
