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
with eu_countries as (
  select *  from {{ ref('countries') }}
), internet_sales as (
  select *  from {{ ref('sales_internet_channel') }}
), customer as (
    select * from {{ source('sh_database', 'customers')}}
)

select  c.cust_first_name, c.cust_last_name, s.time_id, s.prod_id, c.cust_id, s.quantity_sold
from customer c, internet_sales s, eu_countries ct
where c.cust_id = s.cust_id
and c.country_id = ct.country_id

