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
{{config(materialized='view')}}
with direct_sales_promo_cost as(
    SELECT s.prod_id, s.quantity_sold, c.channel_desc, s.amount_sold, p.promo_name, p.promo_cost
    FROM {{ source('sh_database', 'sales') }} s, {{ source('sh_database', 'promotions') }} p, {{ source('sh_database', 'channels') }} c
    WHERE s.channel_id = 3
    AND s.promo_id = p.promo_id
    AND s.channel_id = c.channel_id
)
select * from direct_sales_promo_cost
