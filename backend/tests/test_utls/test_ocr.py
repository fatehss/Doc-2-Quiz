from app.utils.ocr import parse_document
import pytest
import asyncio


@pytest.mark.asyncio
async def test_parse_document():
    document = await parse_document("tests/sample_documents/sample.pdf")
    assert document is not None
    assert len(document) > 0
