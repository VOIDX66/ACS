from pydantic import BaseModel


class JobCreate(BaseModel):
    input_text: str
    priority: int = 0


class JobResponse(BaseModel):
    id: int
    status: str
    priority: int
    input_text: str

    model_config = {"from_attributes": True}


class JobUpdatePriority(BaseModel):
    priority: int


class JobResultResponse(BaseModel):
    job_id: int
    word_count: int
    char_count: int
    processed_text: str
