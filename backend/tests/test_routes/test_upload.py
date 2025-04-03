import pytest
import pytest_asyncio
from bson import ObjectId
from datetime import datetime
from unittest.mock import patch, AsyncMock, MagicMock
import tempfile
import os

# Import the function to test
from app.routes.upload import process_document
from app.db.schemas import Document

# Sample data
SAMPLE_SUBJECT_ID = ObjectId()
SAMPLE_TIME = datetime.now()
SAMPLE_TXT_FILENAME = "test.txt"
SAMPLE_TXT_CONTENT = b"This is text content."
SAMPLE_MD_FILENAME = "test.md"
SAMPLE_MD_CONTENT = b"# Markdown Header"
SAMPLE_PDF_FILENAME = "test.pdf"
SAMPLE_PDF_CONTENT = b"%PDF-..." # Dummy PDF content
MOCKED_OCR_TEXT = "Parsed text from document"

@pytest.mark.asyncio
async def test_process_document_txt():
    """Test processing a .txt file."""
    document = await process_document(
        SAMPLE_TXT_FILENAME, SAMPLE_TXT_CONTENT, SAMPLE_TIME, SAMPLE_SUBJECT_ID
    )
    assert isinstance(document, Document)
    assert document.subject_id == SAMPLE_SUBJECT_ID
    assert document.filename == SAMPLE_TXT_FILENAME
    assert document.ocr_text == SAMPLE_TXT_CONTENT.decode('utf-8')
    assert document.uploaded_at == SAMPLE_TIME
    assert document.metadata == {}
    assert isinstance(document.id, ObjectId)

@pytest.mark.asyncio
async def test_process_document_md():
    """Test processing a .md file."""
    document = await process_document(
        SAMPLE_MD_FILENAME, SAMPLE_MD_CONTENT, SAMPLE_TIME, SAMPLE_SUBJECT_ID
    )
    assert isinstance(document, Document)
    assert document.subject_id == SAMPLE_SUBJECT_ID
    assert document.filename == SAMPLE_MD_FILENAME
    assert document.ocr_text == SAMPLE_MD_CONTENT.decode('utf-8')
    assert document.uploaded_at == SAMPLE_TIME
    assert document.metadata == {}
    assert isinstance(document.id, ObjectId)

@pytest.mark.asyncio
@patch('app.routes.upload.parse_document', new_callable=AsyncMock)
@patch('tempfile.NamedTemporaryFile')
@patch('os.unlink')
async def test_process_document_other_file(mock_unlink, mock_named_temp_file, mock_parse_document):
    """Test processing other file types using mocked LlamaParse."""
    # Configure mocks
    mock_parse_document.return_value = MOCKED_OCR_TEXT

    # Mock the NamedTemporaryFile context manager
    mock_temp_file = MagicMock()
    mock_temp_file.name = "dummy_temp_file.pdf"
    # __enter__ returns the file-like object
    mock_named_temp_file.return_value.__enter__.return_value = mock_temp_file

    document = await process_document(
        SAMPLE_PDF_FILENAME, SAMPLE_PDF_CONTENT, SAMPLE_TIME, SAMPLE_SUBJECT_ID
    )

    # Assertions
    assert isinstance(document, Document)
    assert document.subject_id == SAMPLE_SUBJECT_ID
    assert document.filename == SAMPLE_PDF_FILENAME
    assert document.ocr_text == MOCKED_OCR_TEXT
    assert document.uploaded_at == SAMPLE_TIME
    assert document.metadata == {}
    assert isinstance(document.id, ObjectId)

    # Verify mocks were called correctly
    mock_named_temp_file.assert_called_once_with(delete=False, suffix=".pdf")
    mock_temp_file.write.assert_called_once_with(SAMPLE_PDF_CONTENT)
    mock_temp_file.flush.assert_called_once()
    mock_parse_document.assert_called_once_with(mock_temp_file.name)
    mock_unlink.assert_called_once_with(mock_temp_file.name)

# Tests for process_subject
from app.routes.upload import process_subject
from app.db.schemas import Subject, DocumentRef

# Mock Document returned by process_document
SAMPLE_DOC_1 = Document(
    _id=ObjectId(),
    subject_id=SAMPLE_SUBJECT_ID, # Will be overwritten in mock
    filename="doc1.txt",
    ocr_text="text 1",
    uploaded_at=SAMPLE_TIME, # Will be overwritten in mock
    metadata={}
)
SAMPLE_DOC_2 = Document(
    _id=ObjectId(),
    subject_id=SAMPLE_SUBJECT_ID, # Will be overwritten in mock
    filename="doc2.pdf",
    ocr_text="text 2",
    uploaded_at=SAMPLE_TIME, # Will be overwritten in mock
    metadata={}
)

@pytest.mark.asyncio
@patch('app.routes.upload.process_document', new_callable=AsyncMock)
@patch('app.routes.upload.ObjectId') # Mock ObjectId to control the generated subject_id
@patch('app.routes.upload.datetime') # Mock datetime to control created_at
async def test_process_subject_success(mock_datetime, mock_object_id, mock_process_document, mock_db):
    """Test successful processing of a subject with multiple documents."""
    # Setup mocks
    test_subject_id = ObjectId()
    test_time = datetime(2024, 1, 1, 12, 0, 0)
    mock_object_id.return_value = test_subject_id
    mock_datetime.now.return_value = test_time

    # Configure mock_process_document to return specific documents
    # We need to ensure the subject_id and time match what process_subject generates
    doc1_processed = SAMPLE_DOC_1.model_copy(update={"subject_id": test_subject_id, "uploaded_at": test_time})
    doc2_processed = SAMPLE_DOC_2.model_copy(update={"subject_id": test_subject_id, "uploaded_at": test_time})

    async def side_effect(filename, content, time, subject_id):
        if filename == "doc1.txt":
            return doc1_processed
        elif filename == "doc2.pdf":
            return doc2_processed
        return None

    mock_process_document.side_effect = side_effect

    file_contents = [
        ("doc1.txt", b"content1"),
        ("doc2.pdf", b"content2"),
    ]
    subject_name = "Test Subject"

    # Run the function
    result = await process_subject(file_contents, subject_name)

    # Assertions
    assert result == {"message": "Subject uploaded successfully"}

    # Verify database interactions
    # Check documents inserted
    inserted_docs = list(mock_db.documents.find({}))
    assert len(inserted_docs) == 2
    # Convert BSON documents back to Pydantic models for easier comparison if needed
    # Ensure the correct documents were passed to insert_many (via model_dump)
    assert mock_process_document.call_count == 2

    # Check subject inserted
    inserted_subject = mock_db.subjects.find_one({"_id": test_subject_id})
    assert inserted_subject is not None
    assert inserted_subject["name"] == subject_name
    assert inserted_subject["created_at"] == test_time
    assert len(inserted_subject["documents"]) == 2
    assert inserted_subject["documents"][0]["id"] == doc1_processed.id
    assert inserted_subject["documents"][0]["filename"] == doc1_processed.filename
    assert inserted_subject["documents"][1]["id"] == doc2_processed.id
    assert inserted_subject["documents"][1]["filename"] == doc2_processed.filename

@pytest.mark.asyncio
@patch('app.routes.upload.process_document', new_callable=AsyncMock)
@patch('app.routes.upload.ObjectId')
@patch('app.routes.upload.datetime')
async def test_process_subject_failure_cleanup(mock_datetime, mock_object_id, mock_process_document, mock_db):
    """Test cleanup when process_document raises an exception."""
    # Setup mocks
    test_subject_id = ObjectId()
    test_time = datetime(2024, 1, 1, 12, 0, 0)
    mock_object_id.return_value = test_subject_id
    mock_datetime.now.return_value = test_time

    # Simulate failure in the second document processing
    async def side_effect(filename, content, time, subject_id):
        if filename == "doc1.txt":
            return SAMPLE_DOC_1.model_copy(update={"subject_id": subject_id, "uploaded_at": time})
        elif filename == "doc2.pdf":
            raise ValueError("Processing failed")
        # Explicitly return None for other cases, though not strictly necessary here
        return None
    mock_process_document.side_effect = side_effect

    file_contents = [
        ("doc1.txt", b"content1"),
        ("doc2.pdf", b"content2"),
    ]
    subject_name = "Test Subject Fail"

    # Run the function and expect an exception
    with pytest.raises(ValueError, match="Processing failed"):
        await process_subject(file_contents, subject_name)

    # Verify cleanup - collections should be empty
    assert mock_db.documents.count_documents({}) == 0
    assert mock_db.subjects.count_documents({}) == 0

# Tests for the /upload endpoint
from fastapi import BackgroundTasks
from httpx import AsyncClient
from io import BytesIO

@pytest.mark.asyncio
@patch('app.routes.upload.BackgroundTasks.add_task')
async def test_upload_documents_endpoint(mock_add_task, client: AsyncClient):
    """Test the POST /upload endpoint success case."""
    subject_name = "Endpoint Test Subject"
    file1_content = b"file content 1"
    file2_content = b"file content 2"
    files = {
        'files': [('file1.txt', BytesIO(file1_content), 'text/plain'),
                  ('file2.md', BytesIO(file2_content), 'text/markdown')],
        'name': (None, subject_name)
    }

    response = await client.post("/upload", files=files)

    assert response.status_code == 200
    assert response.json() == {"message": "Documents uploaded successfully"}

    # Verify background task was added with correct arguments
    mock_add_task.assert_called_once()
    # Extract args from call
    call_args, call_kwargs = mock_add_task.call_args
    # First arg is the function (process_subject)
    assert call_args[0].__name__ == 'process_subject'
    # Second arg is file_contents list
    expected_file_contents = [
        ('file1.txt', file1_content),
        ('file2.md', file2_content)
    ]
    assert call_args[1] == expected_file_contents
    # Third arg is the name
    assert call_args[2] == subject_name

@pytest.mark.asyncio
async def test_upload_documents_endpoint_no_files(client: AsyncClient):
    """Test the POST /upload endpoint when no files are provided."""
    response = await client.post("/upload", data={"name": "No Files Subject"})
    # FastAPI/Starlette should return 422 Unprocessable Entity for missing files
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_upload_documents_endpoint_no_name(client: AsyncClient):
    """Test the POST /upload endpoint when the name field is missing."""
    file1_content = b"file content 1"
    files = {
        'files': [('file1.txt', BytesIO(file1_content), 'text/plain')]
        # Missing 'name' field
    }
    response = await client.post("/upload", files=files)
    # FastAPI/Starlette should return 422 Unprocessable Entity for missing form field
    assert response.status_code == 422 