from fastapi import APIRouter, UploadFile, File, BackgroundTasks, Form
from app.db.database import documents_collection, subjects_collection
from app.db.schemas import Subject, Document
from app.utils.ocr import parse_document
from typing import List
import asyncio
from datetime import datetime
from bson.objectid import PyObjectId
from bson import ObjectId
import tempfile
import os

router = APIRouter(prefix="/upload", tags=["upload"])

@router.post("/")
async def upload_documents(background_tasks: BackgroundTasks, files: List[UploadFile] = File(...), name: str = Form(...)):

    background_tasks.add_task(process_subject, files, name)
    return {"message": "Documents uploaded successfully"}

async def process_subject(files: List[UploadFile], name: str):
    '''
    Process a subject by extracting text from each file and creating a list of documents, all in parallel. 
    '''
    time_now = datetime.now()
    subject_id = ObjectId()
    # Create subject with empty document_ids list
    try:
        # Process all documents in parallel
        documents = await asyncio.gather(
            *[process_document(file, time_now, subject_id) for file in files]
        )
        document_ids = [document.id for document in documents]
        # Update subject with document IDs

        documents_collection.insert_many(documents)
        print(f"inserted documents: {document_ids}")
        # Create subject document 
        subjects_collection.insert_one(Subject(
            _id=subject_id,
            name=name,
            created_at=time_now,
            document_ids=document_ids,
            metadata={}
        ))
        
    except Exception as e:
        # In case of failure, attempt to cleanup
        documents_collection.delete_many({"subject_id": subject_id})
        subjects_collection.delete_one({"_id": subject_id})
        raise e

async def process_document(file: UploadFile, time_now: datetime, subject_id: PyObjectId) -> Document:
    '''
    Process a document by extracting text from the image and creating a document object.
    '''
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
        # Write the contents of the uploaded file to the temporary file
        contents = await file.read()
        tmp_file.write(contents)
        tmp_file.flush()
        
        try:
            # Process with LlamaParse
            text = await parse_document(tmp_file.name)
            
            document = Document(
                _id=ObjectId(),
                subject_id=subject_id,
                filename=file.filename,
                ocr_text=text,
                uploaded_at=time_now,
                metadata={}
            )
            return document
        finally:
            # Clean up the temporary file
            os.unlink(tmp_file.name)