"""
ATS scoring service for calculating final scores.
Aggregates all component scores with weighted formula.
"""

import logging
from typing import Dict, List
from app.models.schemas import ScoreBreakdown

logger = logging.getLogger(__name__)


class ScoringService:
    """Service for calculating final ATS scores with weighted components."""

    def __init__(self):
        """Initialize with scoring weights."""
        self.weights = {
            'keyword_match': 0.30,      # 30%
            'semantic_match': 0.25,      # 25%
            'impact_strength': 0.15,     # 15%
            'skills_alignment': 0.10,    # 10%
            'experience_alignment': 0.10, # 10%
            'format_compliance': 0.10     # 10%
        }

        # Validate weights sum to 1.0
        assert abs(sum(self.weights.values()) - 1.0) < 0.001, "Weights must sum to 1.0"

    def calculate_final_score(self, components: Dict[str, float]) -> Dict:
        """
        Calculate final ATS score from component scores.

        Args:
            components: Dictionary with component scores (each 0-100)
                - keyword_match: Keyword coverage score
                - semantic_match: Semantic similarity score
                - impact_strength: Average bullet impact score
                - skills_alignment: Technical skills match score
                - experience_alignment: Experience alignment score
                - format_compliance: Format quality score

        Returns:
            Dictionary with final_score and detailed breakdown
        """
        # Validate all components are present
        for component in self.weights.keys():
            if component not in components:
                logger.warning(f"Missing component: {component}, using 0")
                components[component] = 0.0

        # Calculate weighted contributions
        final_score = 0.0
        breakdown = {}

        for component, weight in self.weights.items():
            score = components[component]

            # Ensure score is in valid range
            score = max(0.0, min(100.0, score))

            contribution = score * weight
            final_score += contribution

            breakdown[component] = {
                'score': round(score, 2),
                'weight': round(weight * 100, 2),
                'contribution': round(contribution, 2)
            }

        # Round final score to integer
        final_score = round(final_score)

        logger.info(f"Calculated final ATS score: {final_score}/100")

        return {
            'final_score': final_score,
            'breakdown': breakdown
        }

    def get_weights(self) -> Dict[str, float]:
        """
        Get scoring weights.

        Returns:
            Dictionary of component weights
        """
        return self.weights.copy()

    def get_grade(self, score: int) -> str:
        """
        Get letter grade for score.

        Args:
            score: ATS score (0-100)

        Returns:
            Letter grade (A+, A, B+, etc.)
        """
        if score >= 95:
            return "A+"
        elif score >= 90:
            return "A"
        elif score >= 85:
            return "A-"
        elif score >= 80:
            return "B+"
        elif score >= 75:
            return "B"
        elif score >= 70:
            return "B-"
        elif score >= 65:
            return "C+"
        elif score >= 60:
            return "C"
        elif score >= 55:
            return "C-"
        elif score >= 50:
            return "D"
        else:
            return "F"

    def get_score_interpretation(self, score: int) -> str:
        """
        Get human-readable interpretation of score.

        Args:
            score: ATS score (0-100)

        Returns:
            Interpretation string
        """
        if score >= 85:
            return "Excellent - Your resume is highly optimized for ATS systems"
        elif score >= 75:
            return "Very Good - Your resume should perform well in ATS screening"
        elif score >= 65:
            return "Good - Your resume is competitive but has room for improvement"
        elif score >= 50:
            return "Fair - Consider implementing the suggested improvements"
        else:
            return "Needs Improvement - Your resume may struggle with ATS screening"

    def identify_top_improvements(self, breakdown: Dict) -> List[Dict]:
        """
        Identify areas needing the most improvement.

        Args:
            breakdown: Score breakdown dictionary

        Returns:
            List of improvement areas sorted by impact
        """
        improvements = []

        for component, data in breakdown.items():
            score = data['score']
            weight = data['weight']

            # Calculate improvement potential (how much score could increase)
            potential_gain = (100 - score) * (weight / 100)

            improvements.append({
                'component': component,
                'current_score': score,
                'weight': weight,
                'potential_gain': round(potential_gain, 2),
                'priority': 'High' if potential_gain > 10 else ('Medium' if potential_gain > 5 else 'Low')
            })

        # Sort by potential gain (descending)
        improvements.sort(key=lambda x: x['potential_gain'], reverse=True)

        return improvements

    def calculate_percentile(self, score: int) -> int:
        """
        Estimate percentile ranking for score.

        Args:
            score: ATS score (0-100)

        Returns:
            Estimated percentile (0-100)
        """
        # Simplified percentile estimation
        # Based on assumption of normal distribution centered around 65
        if score >= 90:
            return 95
        elif score >= 85:
            return 90
        elif score >= 80:
            return 85
        elif score >= 75:
            return 75
        elif score >= 70:
            return 65
        elif score >= 65:
            return 55
        elif score >= 60:
            return 45
        elif score >= 55:
            return 35
        elif score >= 50:
            return 25
        else:
            return max(5, score // 2)

    def compare_to_benchmark(self, score: int, industry: str = "general") -> Dict:
        """
        Compare score to industry benchmarks.

        Args:
            score: ATS score
            industry: Industry category

        Returns:
            Comparison dictionary
        """
        # Simplified benchmarks (would be more sophisticated in production)
        benchmarks = {
            "general": {"low": 50, "average": 65, "high": 80},
            "tech": {"low": 55, "average": 70, "high": 85},
            "finance": {"low": 52, "average": 68, "high": 83},
        }

        benchmark = benchmarks.get(industry, benchmarks["general"])

        if score >= benchmark["high"]:
            comparison = "Above Average"
        elif score >= benchmark["average"]:
            comparison = "Average"
        else:
            comparison = "Below Average"

        return {
            "industry": industry,
            "your_score": score,
            "industry_average": benchmark["average"],
            "comparison": comparison,
            "percentile": self.calculate_percentile(score)
        }
