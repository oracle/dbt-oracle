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
{{
    config(
        materialized='incremental',
        unique_key='group_id')
}}

SELECT prod_name, channel_desc, calendar_month_desc,
   {{ snapshot_hash_arguments(['prod_name', 'channel_desc', 'calendar_month_desc']) }} AS group_id,
   TO_CHAR(SUM(amount_sold), '9,999,999,999') SALES$,
   RANK() OVER (ORDER BY SUM(amount_sold)) AS default_rank,
   RANK() OVER (ORDER BY SUM(amount_sold) DESC NULLS LAST) AS custom_rank
FROM {{ source('sh_database', 'sales') }}, {{ source('sh_database', 'products') }}, {{ source('sh_database', 'customers') }},
     {{ source('sh_database', 'times') }}, {{ source('sh_database', 'channels') }}, {{ source('sh_database', 'countries') }}
WHERE sales.prod_id=products.prod_id AND sales.cust_id=customers.cust_id
  AND customers.country_id = countries.country_id AND sales.time_id=times.time_id
  AND sales.channel_id=channels.channel_id
  AND country_iso_code='US'

{% if is_incremental() %}

  AND times.calendar_month_desc > (SELECT MAX(calendar_month_desc) FROM {{ this }})

{% endif %}

GROUP BY prod_name, channel_desc, calendar_month_desc

