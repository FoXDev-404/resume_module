"""
Text preprocessing service for resume analysis.
Handles text normalization, cleaning, and bullet point extraction.
"""

import re
import logging
from typing import List

from app.utils.text_utils import (
    clean_whitespace,
    normalize_unicode,
    remove_special_characters,
    is_bullet_point,
    strip_bullet_marker
)

logger = logging.getLogger(__name__)


class PreprocessService:
    """Service for preprocessing and cleaning resume/job description text."""

    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text for analysis.

        Args:
            text: Raw text input

        Returns:
            Cleaned and normalized text
        """
        # Normalize Unicode characters
        text = normalize_unicode(text)

        # Normalize whitespace
        text = clean_whitespace(text)

        # Remove excessive newlines (keep max 2 consecutive)
        text = re.sub(r'\n{3,}', '\n\n', text)

        logger.debug(f"Cleaned text: {len(text)} characters")
        return text

    def extract_bullets(self, text: str) -> List[str]:
        """
        Extract bullet points from resume text.

        Args:
            text: Resume text

        Returns:
            List of bullet point strings
        """
        bullets = []
        lines = text.split('\n')
        current_bullet = ""

        for line in lines:
            line_stripped = line.strip()

            if not line_stripped:
                # Empty line - save current bullet if exists
                if current_bullet:
                    bullets.append(current_bullet.strip())
                    current_bullet = ""
                continue

            if is_bullet_point(line_stripped):
                # Save previous bullet if exists
                if current_bullet:
                    bullets.append(current_bullet.strip())

                # Start new bullet
                current_bullet = strip_bullet_marker(line_stripped)
            else:
                # Check if this line continues a bullet
                if current_bullet:
                    # Multi-line bullet continuation
                    current_bullet += " " + line_stripped
                else:
                    # Not a bullet point - check if it looks like an achievement
                    # (starts with action verb, contains content)
                    if len(line_stripped.split()) > 3 and self._starts_with_action_verb(line_stripped):
                        current_bullet = line_stripped

        # Save last bullet
        if current_bullet:
            bullets.append(current_bullet.strip())

        # Filter out very short bullets (likely headers or noise)
        bullets = [b for b in bullets if len(b.split()) >= 3]

        logger.info(f"Extracted {len(bullets)} bullet points")
        return bullets

    def normalize_job_description(self, jd: str) -> str:
        """
        Normalize job description text.

        Args:
            jd: Raw job description

        Returns:
            Cleaned job description
        """
        # Basic cleaning
        jd = self.clean_text(jd)

        # Remove common job posting artifacts
        artifacts = [
            r'apply now',
            r'click here',
            r'send resume to',
            r'equal opportunity employer',
            r'eoe',
        ]

        for artifact in artifacts:
            jd = re.sub(artifact, '', jd, flags=re.IGNORECASE)

        # Clean whitespace again after removals
        jd = clean_whitespace(jd)

        return jd

    def _starts_with_action_verb(self, text: str) -> bool:
        """
        Check if text starts with an action verb.

        Args:
            text: Text to check

        Returns:
            True if starts with action verb
        """
        # Common action verbs
        action_verbs = [
            'achieved', 'administered', 'analyzed', 'architected', 'built', 'collaborated',
            'conducted', 'coordinated', 'created', 'delivered', 'designed', 'developed',
            'directed', 'drove', 'engineered', 'established', 'executed', 'expanded',
            'generated', 'implemented', 'improved', 'increased', 'initiated', 'launched',
            'led', 'managed', 'optimized', 'orchestrated', 'organized', 'performed',
            'pioneered', 'planned', 'produced', 'programmed', 'reduced', 'reengineered',
            'resolved', 'spearheaded', 'streamlined', 'transformed', 'maintained',
            'automated', 'deployed', 'integrated', 'migrated', 'scaled', 'tested',
            'validated', 'monitored', 'documented', 'trained', 'supported', 'enhanced'
        ]

        first_word = text.split()[0].lower().rstrip('.,;:')

        return first_word in action_verbs

    def split_into_words(self, text: str) -> List[str]:
        """
        Split text into individual words.

        Args:
            text: Input text

        Returns:
            List of words
        """
        # Remove punctuation except hyphens in compound words
        text = re.sub(r'[^\w\s\-]', ' ', text)

        # Split on whitespace
        words = text.split()

        # Filter empty strings
        words = [w for w in words if w.strip()]

        return words

    def remove_stop_words(self, words: List[str]) -> List[str]:
        """
        Remove common stop words.

        Args:
            words: List of words

        Returns:
            Filtered list without stop words
        """
        # Common stop words
        stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'the', 'this', 'but', 'they', 'have',
            'had', 'what', 'when', 'where', 'who', 'which', 'why', 'how'
        }

        filtered = [w for w in words if w.lower() not in stop_words]
        return filtered

    def extract_experience_years(self, text: str) -> int:
        """
        Extract years of experience mentioned in text.

        Args:
            text: Resume text

        Returns:
            Years of experience (0 if not found)
        """
        # Patterns like "5+ years", "5 years of experience", etc.
        patterns = [
            r'(\d+)\+?\s*years?',
            r'(\d+)\+?\s*yrs?',
        ]

        years = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            years.extend([int(m) for m in matches])

        # Return maximum years found
        return max(years) if years else 0
