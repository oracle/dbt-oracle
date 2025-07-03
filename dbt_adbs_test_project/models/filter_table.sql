select id,
   label,
   created_at
from {{ ref ('label_data') }}
where id != 2
