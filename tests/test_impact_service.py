"""
Tests for impact analysis service.
"""

import pytest
from app.services.impact_service import ImpactService


class TestImpactService:
    """Test cases for ImpactService."""

    @pytest.fixture
    def impact_service(self):
        """Create impact service instance."""
        return ImpactService()

    def test_detect_quantification_percentage(self, impact_service):
        """Test detection of percentage quantification."""
        bullet = "Increased sales by 25%"
        assert impact_service.detect_quantification(bullet) is True

    def test_detect_quantification_dollar(self, impact_service):
        """Test detection of dollar amount quantification."""
        bullet = "Generated $2M in revenue"
        assert impact_service.detect_quantification(bullet) is True

    def test_detect_quantification_numbers(self, impact_service):
        """Test detection of number quantification."""
        bullet = "Led team of 5 engineers"
        assert impact_service.detect_quantification(bullet) is True

    def test_no_quantification(self, impact_service):
        """Test bullet without quantification."""
        bullet = "Helped with various tasks"
        assert impact_service.detect_quantification(bullet) is False

    def test_detect_weak_verbs(self, impact_service):
        """Test detection of weak verbs."""
        bullet = "Responsible for helping with database tasks"
        weak_patterns = impact_service.detect_weak_patterns(bullet)

        assert len(weak_patterns) > 0
        assert any('responsible' in p or 'helping' in p for p in weak_patterns)

    def test_detect_strong_verb(self, impact_service):
        """Test detection of strong action verbs."""
        bullets_with_strong_verbs = [
            "Led team to deliver project",
            "Architected scalable system",
            "Optimized database performance"
        ]

        for bullet in bullets_with_strong_verbs:
            assert impact_service.detect_strong_verb(bullet) is True

    def test_is_concise(self, impact_service):
        """Test conciseness check."""
        short_bullet = "Led team of 5 engineers to deliver project"
        long_bullet = "Responsible for working alongside the development team to help coordinate and manage various aspects of the project delivery process"

        assert impact_service.is_concise(short_bullet, max_words=25) is True
        assert impact_service.is_concise(long_bullet, max_words=25) is False

    def test_is_active_voice(self, impact_service):
        """Test active voice detection."""
        active = "Led the project team"
        passive = "The project was led by me"

        assert impact_service.is_active_voice(active) is True
        assert impact_service.is_active_voice(passive) is False

    def test_score_strong_bullet(self, impact_service):
        """Test scoring of a strong bullet."""
        bullet = "Led 5-person team to deliver $2M project 3 weeks ahead of schedule"

        score = impact_service.score_bullet_impact(
            has_quantification=True,
            has_strong_verb=True,
            is_concise=True,
            is_active_voice=True,
            has_weak_verb=False
        )

        assert score >= 80  # Should score high

    def test_score_weak_bullet(self, impact_service):
        """Test scoring of a weak bullet."""
        score = impact_service.score_bullet_impact(
            has_quantification=False,
            has_strong_verb=False,
            is_concise=False,
            is_active_voice=False,
            has_weak_verb=True
        )

        assert score <= 30  # Should score low

    @pytest.mark.asyncio
    async def test_analyze_bullet_impact(self, impact_service):
        """Test full bullet analysis."""
        strong_bullet = "Increased revenue by 40% through implementing automated marketing campaigns"

        analysis = impact_service.analyze_bullet_impact(strong_bullet)

        assert 'impact_score' in analysis
        assert 'has_quantification' in analysis
        assert 'weaknesses' in analysis
        assert 'strengths' in analysis

        assert analysis['has_quantification'] is True
        assert analysis['impact_score'] > 50

    @pytest.mark.asyncio
    async def test_analyze_all_bullets(self, impact_service, sample_bullets):
        """Test analysis of multiple bullets."""
        result = await impact_service.analyze_all_bullets(sample_bullets)

        assert 'bullets' in result
        assert 'average_score' in result
        assert 'weak_count' in result
        assert 'strong_count' in result

        assert len(result['bullets']) == len(sample_bullets)
        assert 0 <= result['average_score'] <= 100

    def test_get_weakest_bullets(self, impact_service):
        """Test getting weakest bullets."""
        analyzed_bullets = [
            {'text': 'Bullet 1', 'impact_score': 90},
            {'text': 'Bullet 2', 'impact_score': 30},
            {'text': 'Bullet 3', 'impact_score': 50},
            {'text': 'Bullet 4', 'impact_score': 20}
        ]

        weakest = impact_service.get_weakest_bullets(analyzed_bullets, count=2)

        assert len(weakest) == 2
        assert weakest[0]['impact_score'] == 20
        assert weakest[1]['impact_score'] == 30
