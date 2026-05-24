from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class TextResult:
    id: int
    job_id: int
    word_count: int = 0
    char_count: int = 0
    processed_text: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
