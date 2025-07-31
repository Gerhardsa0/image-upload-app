# schemas.py
from pydantic import BaseModel
from datetime import datetime


class SubmissionResponse(BaseModel):
    id: int
    message: str
    submission_id: str


class SubmissionOut(BaseModel):
    id: int
    user_name: str
    number: float
    image_url: str
    created_at: datetime

    class Config:
        from_attributes = True