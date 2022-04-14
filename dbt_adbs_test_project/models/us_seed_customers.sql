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
with
country AS (select * from {{ source('sh_database', 'countries')}}),
customer AS (select * from {{ source('sh_database', 'customers')}})

select customer.cust_first_name,
       customer.cust_last_name,
       customer.cust_gender,
       customer.cust_marital_status,
       customer.cust_street_address,
       customer.cust_email,
       customer.cust_credit_limit
    from customer, country, {{ ref('income_levels') }} -- refer ephemeral model
    where customer.cust_income_level = {{ ref('income_levels') }}.income_level
    and country.country_iso_code = 'US'
    and customer.country_id = country.country_id
