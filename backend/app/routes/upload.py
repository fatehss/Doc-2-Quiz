from fastapi import APIRouter, UploadFile, File, BackgroundTasks, Form
from app.db.database import documents_collection, subjects_collection
from app.db.schemas import Subject, Document
from app.utils.ocr import parse_document
from typing import List
import asyncio
from datetime import datetime
from bson import ObjectId
import tempfile
import os

router = APIRouter(prefix="/upload", tags=["upload"])

@router.post("")
async def upload_documents(background_tasks: BackgroundTasks, files: List[UploadFile] = File(...), name: str = Form(...)):
    # Read all file contents first
    file_contents = []
    for file in files:
        content = await file.read()
        file_contents.append((file.filename, content))
    
    background_tasks.add_task(process_subject, file_contents, name)
    return {"message": "Documents uploaded successfully"}

async def process_subject(file_contents: List[tuple[str, bytes]], name: str):
    '''
    Process a subject by extracting text from each file and creating a list of documents, all in parallel. 
    '''
    time_now = datetime.now()
    subject_id = ObjectId()
    # Create subject with empty document_ids list
    try:
        # Process all documents in parallel
        documents = await asyncio.gather(
            *[process_document(filename, content, time_now, subject_id) for filename, content in file_contents]
        )
        document_ids = [document.id for document in documents]
        # Update subject with document IDs

        # Convert documents to dictionaries before inserting
        documents_dict = [doc.model_dump(by_alias=True) for doc in documents]
        documents_collection.insert_many(documents_dict)
        print(f"inserted documents: {document_ids}")
        # Create subject document 
        subject = Subject(
            _id=subject_id,
            name=name,
            created_at=time_now,
            document_ids=document_ids,
            metadata={}
        )
        subjects_collection.insert_one(subject.model_dump(by_alias=True))
        print(f"inserted subject: {subject_id}")
        return {"message": "Subject uploaded successfully"}
        
    except Exception as e:
        # In case of failure, attempt to cleanup
        documents_collection.delete_many({"subject_id": subject_id})
        subjects_collection.delete_one({"_id": subject_id})
        raise e

async def process_document(filename: str, content: bytes, time_now: datetime, subject_id: ObjectId) -> Document:
    '''
    Process a document by extracting text from the image and creating a document object.
    If the file is a text or markdown file, return its contents directly.
    '''
    # Get file extension
    _, ext = os.path.splitext(filename)
    ext = ext.lower()

    # For text and markdown files, return content directly
    if ext in ['.txt', '.md']:
        try:
            text = content.decode('utf-8')
        except UnicodeDecodeError:
            # Fallback to a more lenient encoding if UTF-8 fails
            text = content.decode('latin-1')
        
        document = Document(
            _id=ObjectId(),
            subject_id=subject_id,
            filename=filename,
            ocr_text=text,
            uploaded_at=time_now,
            metadata={}
        )
        return document

    # For other files, use LlamaParse
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp_file:
        # Write the contents to the temporary file
        tmp_file.write(content)
        tmp_file.flush()
        
        try:
            # Process with LlamaParse
            text = await parse_document(tmp_file.name)
            
            document = Document(
                _id=ObjectId(),
                subject_id=subject_id,
                filename=filename,
                ocr_text=text,
                uploaded_at=time_now,
                metadata={}
            )
            return document
        finally:
            # Clean up the temporary file
            os.unlink(tmp_file.name)