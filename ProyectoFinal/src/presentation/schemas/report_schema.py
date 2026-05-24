from pydantic import BaseModel


class JobStatusBreakdown(BaseModel):
    total: int
    completed: int
    cancelled: int
    pending: int
    processing: int


class TextProcessingStats(BaseModel):
    total_results: int
    total_words: int
    total_chars: int


class MetricsSummary(BaseModel):
    uptime_seconds: float
    counters: dict[str, int]


class ReportSummary(BaseModel):
    users: int
    jobs: JobStatusBreakdown
    text_processing: TextProcessingStats
    metrics: MetricsSummary


class JobDetailItem(BaseModel):
    job_id: int
    status: str
    priority: int
    input_text: str
    word_count: int
    char_count: int
    created_at: str | None


class UserReportResponse(BaseModel):
    user_id: int
    email: str
    full_name: str
    total_jobs: int
    jobs: list[JobDetailItem]
