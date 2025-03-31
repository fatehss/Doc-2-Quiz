'''
Handles OCR of uploaded documents
'''
import nest_asyncio

nest_asyncio.apply()

from llama_parse import LlamaParse
from typing import Union, List
import os

async def parse_document(file_path: str) -> str:
    """
    Parse a single document using LlamaParse
    """
    parser = LlamaParse(
        api_key=os.getenv("LLAMAPARSE_API_KEY"),
        result_type="markdown",
        verbose=True,
    )

    # Process single file
    documents = await parser.aload_data(file_path)
    
    # Assuming the API returns a list of documents, we'll take the first one
    # You might want to adjust this based on the actual API response
    return documents[0] if documents else ""

    """
    Parse multiple documents using LlamaParse batch processing
    """
    parser = LlamaParse(
        api_key="llx-...",
        result_type="markdown",
        verbose=True,
    )

    # Process batch of files
    documents = await parser.aload_data(file_paths)
    return documents