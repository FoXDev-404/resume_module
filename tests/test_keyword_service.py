"""
Tests for keyword extraction and matching service.
"""

import pytest
from app.services.keyword_service import KeywordService


class TestKeywordService:
    """Test cases for KeywordService."""

    @pytest.fixture
    def keyword_service(self):
        """Create keyword service instance."""
        return KeywordService()

    def test_extract_keywords(self, keyword_service, sample_job_description):
        """Test keyword extraction from job description."""
        keywords = keyword_service.extract_keywords(sample_job_description, top_n=20)

        assert len(keywords) > 0
        assert len(keywords) <= 20
        assert isinstance(keywords, list)

        # Should extract relevant keywords
        keywords_lower = [k.lower() for k in keywords]
        assert any('python' in k or 'engineer' in k for k in keywords_lower)

    def test_categorize_keywords(self, keyword_service):
        """Test keyword categorization."""
        keywords = ['Python', 'JavaScript', 'leadership', 'Docker', 'AWS Certified', 'communication']

        categorized = keyword_service.categorize_keywords(keywords)

        assert 'technical_skills' in categorized
        assert 'soft_skills' in categorized
        assert 'tools' in categorized
        assert 'certifications' in categorized

        # Check proper categorization
        assert 'Python' in categorized['technical_skills']
        assert 'leadership' in categorized['soft_skills']
        assert 'Docker' in categorized['tools']

    def test_match_keywords_exact(self, keyword_service, sample_resume):
        """Test exact keyword matching."""
        keywords = ['Python', 'FastAPI', 'AWS']

        matches = keyword_service.match_keywords(sample_resume, keywords)

        assert 'exact' in matches
        assert 'partial' in matches
        assert 'missing' in matches

        # Python and FastAPI should be in exact matches
        assert 'Python' in matches['exact']
        assert 'FastAPI' in matches['exact']

    def test_match_keywords_missing(self, keyword_service, sample_resume):
        """Test detection of missing keywords."""
        keywords = ['Kubernetes', 'Terraform', 'Go']

        matches = keyword_service.match_keywords(sample_resume, keywords)

        # These keywords should be missing from the sample resume
        for keyword in keywords:
            assert keyword in matches['missing'] or keyword in matches['partial']

    def test_calculate_coverage_score(self, keyword_service):
        """Test keyword coverage score calculation."""
        # 7 out of 10 matched
        score = keyword_service.calculate_coverage_score(7, 10)
        assert score == 70.0

        # All matched
        score = keyword_service.calculate_coverage_score(10, 10)
        assert score == 100.0

        # None matched
        score = keyword_service.calculate_coverage_score(0, 10)
        assert score == 0.0

        # Partial matches
        score = keyword_service.calculate_coverage_score(5.5, 10)
        assert score == 55.0

    def test_calculate_coverage_score_zero_total(self, keyword_service):
        """Test coverage score with zero total keywords."""
        score = keyword_service.calculate_coverage_score(0, 0)
        assert score == 0.0

    def test_calculate_skills_match_score(self, keyword_service, sample_resume):
        """Test technical skills matching score."""
        categorized = {
            'technical_skills': ['Python', 'JavaScript', 'Kubernetes', 'Docker'],
            'soft_skills': [],
            'tools': [],
            'certifications': [],
            'domain_terms': []
        }

        score = keyword_service.calculate_skills_match_score(sample_resume, categorized)

        assert 0 <= score <= 100
        # Python and JavaScript are in resume, Kubernetes is not
        # So score should be moderate
        assert 40 <= score <= 80

    @pytest.mark.asyncio
    async def test_analyze_keywords_integration(
        self,
        keyword_service,
        sample_job_description,
        sample_resume
    ):
        """Test full keyword analysis workflow."""
        result = await keyword_service.analyze_keywords(
            sample_job_description,
            sample_resume,
            top_n=20
        )

        assert 'keywords' in result
        assert 'exact_matches' in result
        assert 'partial_matches' in result
        assert 'missing_keywords' in result
        assert 'coverage_score' in result
        assert 'skills_match_score' in result

        # Verify scores are in valid range
        assert 0 <= result['coverage_score'] <= 100
        assert 0 <= result['skills_match_score'] <= 100

        # Verify categorization
        keywords = result['keywords']
        assert isinstance(keywords, dict)
        assert 'technical_skills' in keywords

    def test_simple_keyword_extraction_fallback(self, keyword_service):
        """Test fallback keyword extraction method."""
        text = "Python developer with React AWS Docker experience. Strong leadership skills."

        keywords = keyword_service._simple_keyword_extraction(text, top_n=5)

        assert len(keywords) <= 5
        assert isinstance(keywords, list)
