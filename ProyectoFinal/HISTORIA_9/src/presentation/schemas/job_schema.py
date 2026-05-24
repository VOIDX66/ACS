from pydantic import BaseModel


class JobCreate(BaseModel):
    input_text: str


class JobResponse(BaseModel):
    id: int
    status: str
    input_text: str

    model_config = {"from_attributes": True}


class JobResultResponse(BaseModel):
    job_id: int
    word_count: int
    char_count: int
    processed_text: str
