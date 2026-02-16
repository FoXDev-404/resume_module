"""
Text processing utilities for resume analysis.
Provides helper functions for string manipulation and cleaning.
"""

import re
from typing import List


def clean_whitespace(text: str) -> str:
    """
    Normalize whitespace in text.

    Args:
        text: Input text with potentially irregular whitespace

    Returns:
        Text with normalized whitespace
    """
    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)
    # Remove leading/trailing whitespace
    text = text.strip()
    return text


def remove_special_characters(text: str, keep_bullets: bool = True) -> str:
    """
    Remove or normalize special characters.

    Args:
        text: Input text
        keep_bullets: If True, preserve bullet point markers

    Returns:
        Cleaned text
    """
    if keep_bullets:
        # Preserve common bullet markers
        text = re.sub(r'[•●○■□▪▫]', '•', text)
    else:
        # Remove all bullet markers
        text = re.sub(r'[•●○■□▪▫\-\*]', '', text)

    # Remove other special characters but keep alphanumeric, punctuation, and whitespace
    # text = re.sub(r'[^\w\s\.\,\;\:\!\?\(\)\[\]\{\}\-\'\"\$\%\@\#]', '', text)

    return text


def normalize_unicode(text: str) -> str:
    """
    Normalize Unicode characters to ASCII equivalents where possible.

    Args:
        text: Input text with potential Unicode characters

    Returns:
        Normalized text
    """
    # Common Unicode replacements
    replacements = {
        '\u2013': '-',  # en dash
        '\u2014': '-',  # em dash
        '\u2018': "'",  # left single quote
        '\u2019': "'",  # right single quote
        '\u201c': '"',  # left double quote
        '\u201d': '"',  # right double quote
        '\u2022': '•',  # bullet point
        '\u00a0': ' ',  # non-breaking space
    }

    for unicode_char, ascii_char in replacements.items():
        text = text.replace(unicode_char, ascii_char)

    return text


def extract_email(text: str) -> str:
    """
    Extract email address from text.

    Args:
        text: Input text potentially containing an email

    Returns:
        Email address if found, empty string otherwise
    """
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    match = re.search(email_pattern, text)
    return match.group(0) if match else ""


def extract_phone(text: str) -> str:
    """
    Extract phone number from text.

    Args:
        text: Input text potentially containing a phone number

    Returns:
        Phone number if found, empty string otherwise
    """
    # Match common phone formats: (555) 123-4567, 555-123-4567, 555.123.4567, etc.
    phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    match = re.search(phone_pattern, text)
    return match.group(0) if match else ""


def split_into_sentences(text: str) -> List[str]:
    """
    Split text into sentences.

    Args:
        text: Input text

    Returns:
        List of sentences
    """
    # Simple sentence splitting on period, exclamation, question mark
    sentences = re.split(r'[.!?]+', text)
    # Clean and filter empty sentences
    sentences = [s.strip() for s in sentences if s.strip()]
    return sentences


def count_words(text: str) -> int:
    """
    Count words in text.

    Args:
        text: Input text

    Returns:
        Word count
    """
    words = text.split()
    return len(words)


def truncate_text(text: str, max_length: int = 500, suffix: str = "...") -> str:
    """
    Truncate text to maximum length.

    Args:
        text: Input text
        max_length: Maximum character length
        suffix: String to append if truncated

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix


def contains_number(text: str) -> bool:
    """
    Check if text contains any numbers.

    Args:
        text: Input text

    Returns:
        True if text contains numbers, False otherwise
    """
    return bool(re.search(r'\d', text))


def extract_numbers(text: str) -> List[str]:
    """
    Extract all numbers from text.

    Args:
        text: Input text

    Returns:
        List of number strings found
    """
    return re.findall(r'\d+(?:\.\d+)?', text)


def lemmatize_word(word: str) -> str:
    """
    Simple lemmatization for common word forms.

    Args:
        word: Word to lemmatize

    Returns:
        Lemmatized word
    """
    word = word.lower()

    # Common suffix removals for simple lemmatization
    if word.endswith('ies'):
        return word[:-3] + 'y'
    elif word.endswith('es'):
        return word[:-2]
    elif word.endswith('s') and not word.endswith('ss'):
        return word[:-1]
    elif word.endswith('ing'):
        return word[:-3]
    elif word.endswith('ed'):
        return word[:-2]

    return word


def is_bullet_point(line: str) -> bool:
    """
    Check if a line appears to be a bullet point.

    Args:
        line: Text line to check

    Returns:
        True if line starts with bullet marker
    """
    line = line.strip()
    # Check for common bullet markers at start
    return bool(re.match(r'^[•●○■□▪▫\-\*]\s+', line))


def strip_bullet_marker(line: str) -> str:
    """
    Remove bullet marker from start of line.

    Args:
        line: Bullet point line

    Returns:
        Line with bullet marker removed
    """
    line = line.strip()
    # Remove bullet markers from start
    return re.sub(r'^[•●○■□▪▫\-\*]\s+', '', line)
