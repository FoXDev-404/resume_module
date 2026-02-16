"""
Tests for scoring service.
"""

import pytest
from app.services.scoring_service import ScoringService


class TestScoringService:
    """Test cases for ScoringService."""

    @pytest.fixture
    def scoring_service(self):
        """Create scoring service instance."""
        return ScoringService()

    def test_weights_sum_to_one(self, scoring_service):
        """Test that all scoring weights sum to 1.0"""
        weights = scoring_service.get_weights()
        total = sum(weights.values())
        assert abs(total - 1.0) < 0.001

    def test_calculate_final_score_perfect(self, scoring_service):
        """Test final score calculation with perfect scores."""
        components = {
            'keyword_match': 100,
            'semantic_match': 100,
            'impact_strength': 100,
            'skills_alignment': 100,
            'experience_alignment': 100,
            'format_compliance': 100
        }

        result = scoring_service.calculate_final_score(components)

        assert result['final_score'] == 100
        assert 'breakdown' in result
        assert len(result['breakdown']) == 6

    def test_calculate_final_score_zero(self, scoring_service):
        """Test final score calculation with zero scores."""
        components = {
            'keyword_match': 0,
            'semantic_match': 0,
            'impact_strength': 0,
            'skills_alignment': 0,
            'experience_alignment': 0,
            'format_compliance': 0
        }

        result = scoring_service.calculate_final_score(components)

        assert result['final_score'] == 0

    def test_calculate_final_score_weighted(self, scoring_service):
        """Test final score with weighted components."""
        components = {
            'keyword_match': 70,      # 30% weight = 21
            'semantic_match': 80,      # 25% weight = 20
            'impact_strength': 65,     # 15% weight = 9.75
            'skills_alignment': 75,    # 10% weight = 7.5
            'experience_alignment': 70, # 10% weight = 7
            'format_compliance': 90    # 10% weight = 9
        }

        result = scoring_service.calculate_final_score(components)

        # Expected: 21 + 20 + 9.75 + 7.5 + 7 + 9 = 74.25 ≈ 74
        assert result['final_score'] == 74

    def test_score_bounds(self, scoring_service):
        """Test that scores are bounded between 0 and 100."""
        # Test with values outside bounds
        components = {
            'keyword_match': 150,      # Above 100
            'semantic_match': -20,     # Below 0
            'impact_strength': 50,
            'skills_alignment': 50,
            'experience_alignment': 50,
            'format_compliance': 50
        }

        result = scoring_service.calculate_final_score(components)

        # Should clamp values
        assert 0 <= result['final_score'] <= 100

    def test_get_grade(self, scoring_service):
        """Test grade assignment."""
        assert scoring_service.get_grade(95) == "A+"
        assert scoring_service.get_grade(90) == "A"
        assert scoring_service.get_grade(85) == "A-"
        assert scoring_service.get_grade(75) == "B"
        assert scoring_service.get_grade(60) == "C"
        assert scoring_service.get_grade(40) == "F"

    def test_get_score_interpretation(self, scoring_service):
        """Test score interpretation messages."""
        interpretation = scoring_service.get_score_interpretation(90)
        assert "Excellent" in interpretation

        interpretation = scoring_service.get_score_interpretation(70)
        assert "Good" in interpretation

        interpretation = scoring_service.get_score_interpretation(40)
        assert "Improvement" in interpretation.lower()

    def test_identify_top_improvements(self, scoring_service):
        """Test identification of improvement areas."""
        breakdown = {
            'keyword_match': {'score': 50, 'weight': 30, 'contribution': 15},
            'semantic_match': {'score': 90, 'weight': 25, 'contribution': 22.5},
            'impact_strength': {'score': 40, 'weight': 15, 'contribution': 6},
            'skills_alignment': {'score': 80, 'weight': 10, 'contribution': 8},
            'experience_alignment': {'score': 70, 'weight': 10, 'contribution': 7},
            'format_compliance': {'score': 95, 'weight': 10, 'contribution': 9.5}
        }

        improvements = scoring_service.identify_top_improvements(breakdown)

        # Should be sorted by potential gain
        assert len(improvements) == 6
        assert improvements[0]['component'] == 'keyword_match'  # Highest potential
        assert improvements[0]['priority'] == 'High'

    def test_calculate_percentile(self, scoring_service):
        """Test percentile calculation."""
        assert scoring_service.calculate_percentile(90) == 95
        assert scoring_service.calculate_percentile(75) == 75
        assert scoring_service.calculate_percentile(50) == 25

    def test_compare_to_benchmark(self, scoring_service):
        """Test benchmark comparison."""
        comparison = scoring_service.compare_to_benchmark(85, "tech")

        assert comparison['industry'] == "tech"
        assert comparison['your_score'] == 85
        assert comparison['comparison'] in ["Above Average", "Average", "Below Average"]
