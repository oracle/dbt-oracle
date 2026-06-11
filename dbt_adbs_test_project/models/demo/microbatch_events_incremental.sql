{#
 Copyright (c) 2026, Oracle and/or its affiliates.

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
        incremental_strategy='microbatch',
        unique_key='event_id',
        event_time='event_time',
        batch_size='day',
        begin=(modules.datetime.datetime.now() - modules.datetime.timedelta(days=2)).replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )
    )
}}

select event_id,
       event_time,
       event_type
from {{ ref('microbatch_events') }}
