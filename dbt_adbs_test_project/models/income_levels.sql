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
config(materialized='ephemeral')
}}
select 'G: 130,000 - 149,999' as income_level from dual
union all
select 'K: 250,000 - 299,999' as income_level from dual
union all
select 'H: 150,000 - 169,999' as income_level from dual
union all
select 'J: 190,000 - 249,999' as income_level from dual
union all
select 'A: Below 30,000' as income_level from dual
