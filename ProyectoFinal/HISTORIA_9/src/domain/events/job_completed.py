from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4


@dataclass
class JobCompletedEvent:
    job_id: int
    user_id: int
    result_summary: str
    event_id: str = field(default_factory=lambda: uuid4().hex[:8])
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
