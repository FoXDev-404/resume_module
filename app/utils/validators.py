"""
Input validation utilities for resume analysis.
Provides validation functions for files and text inputs.
"""

import io
from typing import Optional, Tuple
from fastapi import UploadFile, HTTPException


def validate_file_size(file: UploadFile, max_size_mb: int = 5) -> None:
    """
    Validate uploaded file size.

    Args:
        file: Uploaded file
        max_size_mb: Maximum allowed size in MB

    Raises:
        HTTPException: If file exceeds size limit
    """
    # Read file to check size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to start

    max_bytes = max_size_mb * 1024 * 1024

    if file_size > max_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {max_size_mb}MB, got {file_size / 1024 / 1024:.2f}MB"
        )


def validate_file_type(file: UploadFile, allowed_types: list = None) -> None:
    """
    Validate uploaded file type.

    Args:
        file: Uploaded file
        allowed_types: List of allowed file extensions

    Raises:
        HTTPException: If file type is not allowed
    """
    if allowed_types is None:
        allowed_types = [".pdf", ".txt"]

    if not file.filename:
        raise HTTPException(status_code=400, detail="File name is required")

    # Get file extension
    file_ext = "." + file.filename.split(".")[-1].lower() if "." in file.filename else ""

    if file_ext not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(allowed_types)}, got {file_ext}"
        )


def validate_pdf_content(content: bytes) -> None:
    """
    Validate that content is a valid PDF.

    Args:
        content: File content bytes

    Raises:
        HTTPException: If content is not a valid PDF
    """
    # Check PDF magic number
    if not content.startswith(b'%PDF'):
        raise HTTPException(
            status_code=400,
            detail="Invalid PDF file. File does not have PDF header."
        )

    # Basic size check
    if len(content) < 100:
        raise HTTPException(
            status_code=400,
            detail="PDF file appears to be corrupted or empty"
        )


def validate_text_length(text: str, min_length: int = 50, max_length: int = 50000,
                        field_name: str = "Text") -> None:
    """
    Validate text length.

    Args:
        text: Input text
        min_length: Minimum required length
        max_length: Maximum allowed length
        field_name: Name of field for error messages

    Raises:
        HTTPException: If text length is invalid
    """
    text = text.strip()
    length = len(text)

    if length < min_length:
        raise HTTPException(
            status_code=400,
            detail=f"{field_name} too short. Minimum {min_length} characters, got {length}"
        )

    if length > max_length:
        raise HTTPException(
            status_code=400,
            detail=f"{field_name} too long. Maximum {max_length} characters, got {length}"
        )


def validate_resume_input(
    resume_file: Optional[UploadFile] = None,
    resume_text: Optional[str] = None
) -> Tuple[str, str]:
    """
    Validate that either resume file or text is provided.

    Args:
        resume_file: Uploaded resume file
        resume_text: Resume text input

    Returns:
        Tuple of (content, source_type) where source_type is 'file' or 'text'

    Raises:
        HTTPException: If neither or invalid input provided
    """
    if not resume_file and not resume_text:
        raise HTTPException(
            status_code=400,
            detail="Please provide either a resume file or resume text"
        )

    if resume_file and resume_text:
        raise HTTPException(
            status_code=400,
            detail="Please provide only one of: resume file OR resume text, not both"
        )

    if resume_file:
        return "file", "file"
    else:
        # Validate text length
        if not resume_text or not resume_text.strip():
            raise HTTPException(
                status_code=400,
                detail="Resume text cannot be empty"
            )
        return "text", "text"


def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent injection attacks.

    Args:
        text: User input text

    Returns:
        Sanitized text
    """
    # Remove any potential script tags or HTML
    text = text.replace('<', '&lt;').replace('>', '&gt;')

    # Remove null bytes
    text = text.replace('\x00', '')

    return text.strip()
