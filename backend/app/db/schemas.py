from pydantic import BaseModel, Field
from typing import List, Optional
from bson import ObjectId
import datetime
from uuid import UUID, uuid4
import uuid

# Document Schema
class Document(BaseModel):
    id: ObjectId = Field(default_factory=ObjectId, alias="_id")
    subject_id: ObjectId
    filename: str
    ocr_text: str
    uploaded_at: datetime.datetime
    metadata: dict
    class Config:
        arbitrary_types_allowed = True
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}

# Subject Schema
class Subject(BaseModel):
    id: ObjectId = Field(default_factory=ObjectId, alias="_id")
    user_id: str | None = None
    name: str
    created_at: datetime.datetime
    document_ids: List[ObjectId]
    metadata: dict
    class Config:
        arbitrary_types_allowed = True
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}

class Question(BaseModel):
    id: UUID = Field(default_factory=uuid.uuid4)
    question: str
    choices: List[str]
    answer: str
    explanation: str | None = None
    metadata: dict


class Quiz(BaseModel):
    id: ObjectId = Field(default_factory=ObjectId, alias="_id")
    subject_ids: List[ObjectId]
    created_at: datetime.datetime
    updated_at: datetime.datetime
    status: str = Field(default="pending")
    score: float | None = None
    questions: List[Question]
    metadata: dict
    class Config:
        arbitrary_types_allowed = True
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}

