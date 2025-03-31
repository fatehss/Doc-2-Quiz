from pydantic import BaseModel, Field
from typing import List, Optional
from bson import ObjectId
import datetime
from uuid import UUID, uuid4
import uuid
# MongoDB ID compatibility
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError('Invalid objectid')
        return ObjectId(v)

# Document Schema
class Document(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    subject_id: PyObjectId
    filename: str
    ocr_text: str
    uploaded_at: datetime.datetime
    metadata: dict
    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}

# Subject Schema
class Subject(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str | None = None
    name: str
    created_at: datetime.datetime
    document_ids: List[PyObjectId]
    metadata: dict
    class Config:
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
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    subject_ids: List[PyObjectId]
    created_at: datetime.datetime
    updated_at: datetime.datetime
    status: str = Field(default="pending")
    score: float | None = None
    questions: List[Question]
    metadata: dict
    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}

