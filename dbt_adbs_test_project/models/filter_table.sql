select id,
   label,
   created_at
from {{ ref ('dummy_model') }}
where id != 2
