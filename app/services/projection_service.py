"""
Score projection service for simulating improvements.
Calculates projected scores after applying optimizations.
"""

import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class ProjectionService:
    """Service for projecting score improvements after optimizations."""

    def project_improved_score(
        self,
        current_score: int,
        current_breakdown: Dict,
        rewrites: List[Dict],
        original_bullets: List[Dict],
        missing_keywords: List[str],
        total_keywords: int
    ) -> Dict:
        """
        Project improved score after applying rewrites.

        Args:
            current_score: Current ATS score
            current_breakdown: Current score breakdown
            rewrites: List of bullet rewrites
            original_bullets: Original bullet analyses
            missing_keywords: List of missing keywords
            total_keywords: Total number of JD keywords

        Returns:
            Projection results with new score and improvements
        """
        # Calculate new impact score
        new_impact_score = self._calculate_new_impact_score(
            original_bullets, rewrites
        )

        # Calculate new keyword coverage
        new_keyword_score = self._calculate_new_keyword_coverage(
            current_breakdown.get('keyword_match', {}).get('score', 0),
            rewrites,
            missing_keywords,
            total_keywords
        )

        # Get current component scores
        current_components = {
            'keyword_match': current_breakdown.get('keyword_match', {}).get('score', 0),
            'semantic_match': current_breakdown.get('semantic_match', {}).get('score', 0),
            'impact_strength': current_breakdown.get('impact_strength', {}).get('score', 0),
            'skills_alignment': current_breakdown.get('skills_alignment', {}).get('score', 0),
            'experience_alignment': current_breakdown.get('experience_alignment', {}).get('score', 0),
            'format_compliance': current_breakdown.get('format_compliance', {}).get('score', 0),
        }

        # Update with projected improvements
        projected_components = current_components.copy()
        projected_components['impact_strength'] = new_impact_score
        projected_components['keyword_match'] = new_keyword_score

        # Calculate new final score
        from app.services.scoring_service import ScoringService
        scoring_service = ScoringService()
        projected_result = scoring_service.calculate_final_score(projected_components)

        projected_score = projected_result['final_score']
        improvement = projected_score - current_score
        percentage_gain = (improvement / current_score * 100) if current_score > 0 else 0

        # Calculate component-level improvements
        component_improvements = {
            'impact_strength': new_impact_score - current_components['impact_strength'],
            'keyword_coverage': new_keyword_score - current_components['keyword_match']
        }

        logger.info(
            f"Projected score: {projected_score} (current: {current_score}, "
            f"improvement: +{improvement}, {percentage_gain:.1f}%)"
        )

        return {
            'current_score': current_score,
            'projected_score': projected_score,
            'improvement': improvement,
            'percentage_gain': round(percentage_gain, 2),
            'breakdown': component_improvements
        }

    def _calculate_new_impact_score(
        self,
        original_bullets: List[Dict],
        rewrites: List[Dict]
    ) -> float:
        """
        Calculate new average impact score with rewrites applied.

        Args:
            original_bullets: Original bullet analyses
            rewrites: Rewritten bullets

        Returns:
            New average impact score
        """
        if not original_bullets:
            return 0.0

        # Create a mapping of original text to rewrite
        rewrite_map = {r['original']: 95 for r in rewrites}  # Assume rewrites score ~95

        # Calculate new scores
        total_score = 0
        count = 0

        for bullet in original_bullets:
            bullet_text = bullet.get('text', '')
            if bullet_text in rewrite_map:
                # Use projected high score for rewritten bullet
                total_score += rewrite_map[bullet_text]
            else:
                # Keep original score
                total_score += bullet.get('impact_score', 0)

            count += 1

        new_avg = total_score / count if count > 0 else 0
        return round(new_avg, 2)

    def _calculate_new_keyword_coverage(
        self,
        current_coverage: float,
        rewrites: List[Dict],
        missing_keywords: List[str],
        total_keywords: int
    ) -> float:
        """
        Calculate new keyword coverage after rewrites.

        Args:
            current_coverage: Current keyword coverage score
            rewrites: Rewritten bullets with keywords added
            missing_keywords: Original missing keywords
            total_keywords: Total number of keywords from JD

        Returns:
            New keyword coverage score
        """
        if total_keywords == 0:
            return current_coverage

        # Count how many keywords were added
        added_keywords = set()
        for rewrite in rewrites:
            for keyword in rewrite.get('keywords_added', []):
                added_keywords.add(keyword.lower())

        # Calculate additional coverage
        additional_matches = len(added_keywords)

        # Calculate current number of matches from coverage percentage
        current_matches = (current_coverage / 100) * total_keywords

        # Calculate new matches
        new_matches = min(current_matches + additional_matches, total_keywords)

        # Calculate new coverage
        new_coverage = (new_matches / total_keywords) * 100

        return round(new_coverage, 2)

    def calculate_roi(
        self,
        current_score: int,
        projected_score: int,
        time_to_apply_minutes: int = 15
    ) -> Dict:
        """
        Calculate return on investment for applying changes.

        Args:
            current_score: Current score
            projected_score: Projected score after changes
            time_to_apply_minutes: Estimated time to apply changes

        Returns:
            ROI analysis
        """
        improvement = projected_score - current_score

        # Simple ROI metric: points gained per minute of effort
        roi = improvement / time_to_apply_minutes if time_to_apply_minutes > 0 else 0

        return {
            'improvement_points': improvement,
            'time_required_minutes': time_to_apply_minutes,
            'roi_points_per_minute': round(roi, 2),
            'recommendation': 'Highly Recommended' if roi > 0.5 else ('Recommended' if roi > 0.25 else 'Optional')
        }

    def estimate_application_success_rate(self, score: int) -> Dict:
        """
        Estimate likelihood of passing ATS screening at different score levels.

        Args:
            score: ATS score

        Returns:
            Success rate estimates
        """
        # Simplified estimates (would be based on real data in production)
        if score >= 85:
            pass_rate = 90
            tier = "High"
        elif score >= 75:
            pass_rate = 75
            tier = "Medium-High"
        elif score >= 65:
            pass_rate = 60
            tier = "Medium"
        elif score >= 50:
            pass_rate = 40
            tier = "Medium-Low"
        else:
            pass_rate = 20
            tier = "Low"

        return {
            'score': score,
            'estimated_pass_rate': pass_rate,
            'tier': tier,
            'interpretation': f"{pass_rate}% chance of passing ATS screening"
        }

    def compare_before_after(
        self,
        current_score: int,
        projected_score: int
    ) -> Dict:
        """
        Generate before/after comparison summary.

        Args:
            current_score: Current score
            projected_score: Projected score

        Returns:
            Comparison summary
        """
        current_success = self.estimate_application_success_rate(current_score)
        projected_success = self.estimate_application_success_rate(projected_score)

        improvement_rate = projected_success['estimated_pass_rate'] - current_success['estimated_pass_rate']

        return {
            'current': {
                'score': current_score,
                'pass_rate': current_success['estimated_pass_rate'],
                'tier': current_success['tier']
            },
            'projected': {
                'score': projected_score,
                'pass_rate': projected_success['estimated_pass_rate'],
                'tier': projected_success['tier']
            },
            'improvement': {
                'score_points': projected_score - current_score,
                'pass_rate_points': improvement_rate,
                'tier_change': f"{current_success['tier']} → {projected_success['tier']}"
            }
        }
