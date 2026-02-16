"""
Pytest configuration and fixtures for testing Resume Optimization SaaS.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock

# Import the app
from app.main import app


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def sample_resume():
    """Sample resume text for testing."""
    return """
    John Doe
    john.doe@email.com | (555) 123-4567

    PROFESSIONAL SUMMARY
    Experienced software engineer with 5+ years of Python development.

    EXPERIENCE
    Senior Software Engineer | Tech Corp | 2020-Present
    • Led team of 5 engineers to deliver cloud migration project
    • Helped with testing and bug fixes
    • Worked on database optimization
    • Implemented RESTful APIs using Python and FastAPI
    • Reduced application latency by 40% through caching strategies

    Software Engineer | StartupCo | 2018-2020
    • Developed web applications using React and Node.js
    • Responsible for maintaining CI/CD pipelines
    • Participated in agile development processes

    EDUCATION
    B.S. Computer Science | University Name | 2018

    SKILLS
    Python, JavaScript, React, AWS, Git, Docker
    """


@pytest.fixture
def sample_job_description():
    """Sample job description for testing."""
    return """
    Senior Software Engineer

    We are looking for an experienced Senior Software Engineer to join our team.

    REQUIREMENTS:
    • 5+ years of professional software development experience
    • Strong proficiency in Python, Docker, and Kubernetes
    • Experience with cloud platforms (AWS, GCP, or Azure)
    • Familiarity with microservices architecture
    • Strong leadership and communication skills
    • Experience with CI/CD pipelines and DevOps practices

    NICE TO HAVE:
    • Experience with machine learning or AI
    • Open source contributions
    • AWS certifications

    RESPONSIBILITIES:
    • Lead development of scalable backend systems
    • Mentor junior engineers
    • Design and implement RESTful APIs
    • Optimize database performance
    • Collaborate with cross-functional teams
    """


@pytest.fixture
def mock_gemini_embedding():
    """Mock Gemini embedding response."""
    # Return a fixed embedding vector (768 dimensions)
    return [0.1] * 768


@pytest.fixture
def mock_gemini_text_response():
    """Mock Gemini text generation response."""
    return '{"gaps": ["Leadership experience is mentioned in job description but not highlighted in resume", "Kubernetes experience is required but not mentioned", "No mention of microservices architecture"]}'


@pytest.fixture
def mock_gemini_rewrite():
    """Mock Gemini bullet rewrite response."""
    return "Led 5-person engineering team to successfully deliver cloud migration project 2 weeks ahead of schedule using AWS and Docker"


@pytest.fixture
def sample_bullets():
    """Sample bullet points for testing."""
    return [
        "Led team of 5 engineers to deliver cloud migration project",
        "Helped with testing and bug fixes",
        "Worked on database optimization",
        "Reduced application latency by 40% through caching strategies"
    ]


@pytest.fixture
def weak_bullet():
    """Weak bullet point for testing."""
    return "Responsible for helping with various tasks"


@pytest.fixture
def strong_bullet():
    """Strong bullet point for testing."""
    return "Led 5-person team to deliver $2M cloud migration project 3 weeks ahead of schedule"


@pytest.fixture
async def mock_embedding_service(monkeypatch, mock_gemini_embedding, mock_gemini_text_response):
    """Mock Gemini API calls for testing."""
    from app.services import embedding_service

    # Mock embedding generation
    async def mock_get_embedding(self, text):
        return mock_gemini_embedding

    # Mock text generation
    async def mock_call_gemini(self, prompt):
        return mock_gemini_text_response

    monkeypatch.setattr(
        embedding_service.EmbeddingService,
        'get_embedding',
        mock_get_embedding
    )

    monkeypatch.setattr(
        embedding_service.EmbeddingService,
        '_call_gemini_with_retry',
        mock_call_gemini
    )


# Skip tests that require actual Gemini API
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test (may call external APIs)"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
