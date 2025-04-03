import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
import mongomock
from motor.motor_asyncio import AsyncIOMotorClient
from app.server import app
from app.db import database
from dotenv import load_dotenv

load_dotenv()

# Store original database clients
original_client = database.client
original_db = database.db
original_documents_collection = database.documents_collection
original_subjects_collection = database.subjects_collection

@pytest.fixture(scope="function", autouse=True)
def mock_mongo_client(monkeypatch):
    """Mocks the MongoDB client for each test function."""
    mock_client = mongomock.MongoClient()
    mock_db = mock_client["test_doc_2_quiz"]

    # Mock the database objects used in the application
    monkeypatch.setattr(database, "client", mock_client)
    monkeypatch.setattr(database, "db", mock_db)
    # Assuming collections are accessed via database.db
    monkeypatch.setattr(database, "documents_collection", mock_db.documents)
    monkeypatch.setattr(database, "subjects_collection", mock_db.subjects)

    # Ensure collections are clean before tests start (redundant now with mock_db fixture, but harmless)
    mock_db.documents.drop()
    mock_db.subjects.drop()

    yield mock_client  # Provide the mock client to tests if needed

    # Cleanup: Restore original database client and drop mock collections after tests
    # Monkeypatch handles restoration automatically when the function scope ends
    mock_db.documents.drop()
    mock_db.subjects.drop()
    # No need to manually restore with monkeypatch.setattr here, it's handled by pytest


@pytest_asyncio.fixture(scope="function")
async def client():
    """Creates an async test client for FastAPI."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

@pytest.fixture(scope="function")
def mock_db(mock_mongo_client):
    """Provides the mock database instance for function scope, ensuring clean state."""
    db = mock_mongo_client["test_doc_2_quiz"]
    # Clear collections before each test function
    db.documents.drop()
    db.subjects.drop()
    return db
