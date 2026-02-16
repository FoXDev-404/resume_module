"""
Resume parsing service for PDF and text extraction.
Handles file parsing, text extraction, and format validation.
"""

import io
import re
import logging
from typing import Dict, Optional
from fastapi import UploadFile, HTTPException
import pdfplumber

from app.utils.text_utils import (
    normalize_unicode,
    clean_whitespace,
    extract_email,
    extract_phone
)
from app.utils.validators import (
    validate_file_size,
    validate_file_type,
    validate_pdf_content
)

logger = logging.getLogger(__name__)


class ParserService:
    """Service for parsing resumes from various file formats."""

    async def parse_resume(self, file: Optional[UploadFile] = None, text: Optional[str] = None) -> str:
        """
        Parse resume from file upload or direct text input.

        Args:
            file: Uploaded PDF or text file
            text: Direct text input

        Returns:
            Extracted resume text

        Raises:
            HTTPException: If parsing fails or file is invalid
        """
        if file:
            return await self.parse_file(file)
        elif text:
            return self.parse_text(text)
        else:
            raise HTTPException(status_code=400, detail="No resume provided")

    async def parse_file(self, file: UploadFile) -> str:
        """
        Parse resume from uploaded file.

        Args:
            file: Uploaded file (PDF or TXT)

        Returns:
            Extracted text

        Raises:
            HTTPException: If file is invalid or parsing fails
        """
        # Validate file
        validate_file_size(file, max_size_mb=5)
        validate_file_type(file, allowed_types=[".pdf", ".txt"])

        # Read file content
        content = await file.read()

        # Determine file type and parse accordingly
        if file.filename and file.filename.lower().endswith('.pdf'):
            return await self.parse_pdf(content)
        else:
            return self.parse_text(content.decode('utf-8'))

    async def parse_pdf(self, content: bytes) -> str:
        """
        Extract text from PDF file.

        Args:
            content: PDF file content as bytes

        Returns:
            Extracted text from PDF

        Raises:
            HTTPException: If PDF is corrupted or cannot be parsed
        """
        # Validate PDF
        validate_pdf_content(content)

        try:
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                if len(pdf.pages) == 0:
                    raise HTTPException(
                        status_code=400,
                        detail="PDF contains no pages"
                    )

                # Extract text from all pages
                text_parts = []
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)

                # Combine all pages
                full_text = "\n".join(text_parts)

                if not full_text.strip():
                    raise HTTPException(
                        status_code=400,
                        detail="Could not extract text from PDF. It may be image-based or empty."
                    )

                # Clean and normalize
                full_text = normalize_unicode(full_text)
                logger.info(f"Successfully extracted {len(full_text)} characters from PDF")

                return full_text

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"PDF parsing failed: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to parse PDF: {str(e)}"
            )

    def parse_text(self, text: str) -> str:
        """
        Process plain text resume input.

        Args:
            text: Resume text

        Returns:
            Cleaned text

        Raises:
            HTTPException: If text is empty
        """
        text = text.strip()
        if not text:
            raise HTTPException(status_code=400, detail="Resume text is empty")

        # Normalize Unicode
        text = normalize_unicode(text)

        logger.info(f"Parsed text resume with {len(text)} characters")
        return text

    def extract_sections(self, text: str) -> Dict[str, str]:
        """
        Extract major sections from resume text.

        Args:
            text: Resume text

        Returns:
            Dictionary with section names as keys and content as values
        """
        sections = {
            'experience': '',
            'education': '',
            'skills': '',
            'summary': '',
            'other': ''
        }

        # Common section headers (case-insensitive patterns)
        section_patterns = {
            'experience': r'(?i)(work experience|professional experience|employment|experience)',
            'education': r'(?i)(education|academic background)',
            'skills': r'(?i)(skills|technical skills|core competencies)',
            'summary': r'(?i)(summary|profile|objective|about)'
        }

        # Try to identify sections
        lines = text.split('\n')
        current_section = 'other'

        for line in lines:
            line_stripped = line.strip()

            # Check if line is a section header
            for section_name, pattern in section_patterns.items():
                if re.match(pattern, line_stripped):
                    current_section = section_name
                    break

            # Add line to current section
            if line_stripped:
                sections[current_section] += line + '\n'

        return {k: v.strip() for k, v in sections.items() if v.strip()}

    def format_compliance_score(self, text: str) -> float:
        """
        Calculate format compliance score based on resume structure.

        Args:
            text: Resume text

        Returns:
            Format compliance score (0-100)
        """
        score = 0.0

        # Check for contact information (30 points)
        email = extract_email(text)
        phone = extract_phone(text)

        if email:
            score += 15
        if phone:
            score += 15

        # Check for sections (45 points total, 15 each)
        sections_found = 0
        section_keywords = ['experience', 'education', 'skills']

        for keyword in section_keywords:
            if re.search(rf'\b{keyword}\b', text, re.IGNORECASE):
                sections_found += 1
                score += 15

        # Check for bullet points (25 points)
        bullet_pattern = r'[•●○■□▪▫\-\*]\s+'
        if re.search(bullet_pattern, text):
            score += 25

        logger.debug(f"Format compliance score: {score}/100")
        return min(score, 100.0)

    def has_contact_info(self, text: str) -> bool:
        """
        Check if resume contains contact information.

        Args:
            text: Resume text

        Returns:
            True if contact info found, False otherwise
        """
        has_email = bool(extract_email(text))
        has_phone = bool(extract_phone(text))
        return has_email or has_phone
