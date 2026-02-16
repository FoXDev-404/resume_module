"""
Impact analysis service for resume bullet points.
Analyzes bullet strength based on quantification, action verbs, and conciseness.
"""

import re
import logging
from typing import Dict, List
from app.models.schemas import BulletAnalysis

logger = logging.getLogger(__name__)


class ImpactService:
    """Service for analyzing the impact strength of resume bullet points."""

    def __init__(self):
        """Initialize with action verb dictionaries."""
        # Strong action verbs
        self.strong_verbs = {
            'achieved', 'accelerated', 'accomplished', 'architected', 'automated',
            'built', 'championed', 'created', 'delivered', 'designed', 'developed',
            'directed', 'drove', 'eliminated', 'engineered', 'established', 'executed',
            'expanded', 'generated', 'implemented', 'improved', 'increased', 'initiated',
            'launched', 'led', 'managed', 'orchestrated', 'optimized', 'pioneered',
            'produced', 'reduced', 'reengineered', 'resolved', 'scaled', 'spearheaded',
            'streamlined', 'transformed', 'upgraded', 'overhauled', 'maximized',
            'minimized', 'modernized', 'revolutionized'
        }

        # Weak action verbs/phrases
        self.weak_verbs = {
            'responsible for', 'worked on', 'helped', 'helped with', 'assisted',
            'assisted with', 'participated', 'participated in', 'involved in',
            'dealt with', 'handled', 'tasked with', 'duties included'
        }

    async def analyze_all_bullets(self, bullets: List[str]) -> Dict:
        """
        Analyze all bullet points from a resume.

        Args:
            bullets: List of bullet point strings

        Returns:
            Dictionary with bullet analyses and average score
        """
        if not bullets:
            return {
                'bullets': [],
                'average_score': 0,
                'weak_count': 0,
                'strong_count': 0
            }

        analyzed_bullets = []
        total_score = 0

        for bullet in bullets:
            analysis = self.analyze_bullet_impact(bullet)
            analyzed_bullets.append(analysis)
            total_score += analysis['impact_score']

        average = total_score / len(bullets) if bullets else 0
        weak_count = sum(1 for b in analyzed_bullets if b['impact_score'] < 50)
        strong_count = sum(1 for b in analyzed_bullets if b['impact_score'] >= 70)

        logger.info(f"Analyzed {len(bullets)} bullets - Avg score: {average:.1f}, Weak: {weak_count}, Strong: {strong_count}")

        return {
            'bullets': analyzed_bullets,
            'average_score': round(average, 2),
            'weak_count': weak_count,
            'strong_count': strong_count
        }

    def analyze_bullet_impact(self, bullet: str) -> Dict:
        """
        Analyze impact strength of a single bullet point.

        Args:
            bullet: Bullet point text

        Returns:
            Dictionary with impact score and analysis details
        """
        bullet_lower = bullet.lower()

        # Detect features
        has_quantification = self.detect_quantification(bullet)
        weak_patterns = self.detect_weak_patterns(bullet)
        has_strong_verb = self.detect_strong_verb(bullet)
        is_concise = self.is_concise(bullet)
        is_active_voice = self.is_active_voice(bullet)

        # Calculate score
        score = self.score_bullet_impact(
            has_quantification=has_quantification,
            has_strong_verb=has_strong_verb,
            is_concise=is_concise,
            is_active_voice=is_active_voice,
            has_weak_verb=bool(weak_patterns)
        )

        # Identify weaknesses and strengths
        weaknesses = []
        strengths = []

        if not has_quantification:
            weaknesses.append("no quantifiable metrics")
        else:
            strengths.append("contains metrics")

        if weak_patterns:
            weaknesses.extend([f"weak phrase: '{p}'" for p in weak_patterns])

        if has_strong_verb:
            strengths.append("strong action verb")
        elif not weak_patterns:
            weaknesses.append("no strong action verb")

        if not is_concise:
            weaknesses.append("too verbose")
        else:
            strengths.append("concise")

        if not is_active_voice:
            weaknesses.append("passive voice")
        else:
            strengths.append("active voice")

        return {
            'text': bullet,
            'impact_score': score,
            'has_quantification': has_quantification,
            'weaknesses': weaknesses,
            'strengths': strengths
        }

    def detect_quantification(self, bullet: str) -> bool:
        """
        Detect if bullet contains quantifiable metrics.

        Args:
            bullet: Bullet point text

        Returns:
            True if quantification detected
        """
        # Patterns for quantification
        patterns = [
            r'\d+%',  # 25%
            r'\$\d+',  # $100
            r'\d+\s*(million|thousand|billion|k|m|b)\b',  # 5 million
            r'\d+\+',  # 10+
            r'\d+x',  # 2x
            r'\d+\s*(percent|percentage)',  # 50 percent
            r'\b\d+\s*(users|customers|clients|projects|people|team members|employees)\b',  # 100 users
            r'\d+\s*(hours|days|weeks|months|years)',  # 3 months
            r'(increased|reduced|improved|decreased|grew)\s+by\s+\d+',  # increased by 50
        ]

        for pattern in patterns:
            if re.search(pattern, bullet, re.IGNORECASE):
                return True

        return False

    def detect_weak_patterns(self, bullet: str) -> List[str]:
        """
        Detect weak verbs and phrases.

        Args:
            bullet: Bullet point text

        Returns:
            List of detected weak patterns
        """
        bullet_lower = bullet.lower()
        found_weak = []

        for weak in self.weak_verbs:
            if weak in bullet_lower:
                found_weak.append(weak)

        return found_weak

    def detect_strong_verb(self, bullet: str) -> bool:
        """
        Detect strong action verbs.

        Args:
            bullet: Bullet point text

        Returns:
            True if strong verb detected
        """
        bullet_lower = bullet.lower()

        # Check if bullet starts with or contains strong verb
        for verb in self.strong_verbs:
            if re.search(r'\b' + verb + r'\b', bullet_lower):
                return True

        return False

    def is_concise(self, bullet: str, max_words: int = 25) -> bool:
        """
        Check if bullet is concise.

        Args:
            bullet: Bullet point text
            max_words: Maximum word count for conciseness

        Returns:
            True if concise
        """
        word_count = len(bullet.split())
        return word_count <= max_words

    def is_active_voice(self, bullet: str) -> bool:
        """
        Check if bullet uses active voice.

        Args:
            bullet: Bullet point text

        Returns:
            True if active voice (no passive indicators)
        """
        # Passive voice indicators
        passive_patterns = [
            r'\bwas\s+\w+ed\b',  # was created
            r'\bwere\s+\w+ed\b',  # were implemented
            r'\bbeen\s+\w+ed\b',  # been deployed
            r'\bis\s+\w+ed\b',  # is managed
            r'\bare\s+\w+ed\b',  # are handled
        ]

        for pattern in passive_patterns:
            if re.search(pattern, bullet, re.IGNORECASE):
                return False

        return True

    def score_bullet_impact(
        self,
        has_quantification: bool,
        has_strong_verb: bool,
        is_concise: bool,
        is_active_voice: bool,
        has_weak_verb: bool
    ) -> int:
        """
        Calculate impact score based on bullet features.

        Scoring:
        - Quantification: +40 points
        - Strong action verb: +30 points
        - Concise: +20 points
        - Active voice: +10 points
        - Penalty for weak verb: -20 points

        Args:
            has_quantification: Contains metrics
            has_strong_verb: Contains strong action verb
            is_concise: Is concise (<= 25 words)
            is_active_voice: Uses active voice
            has_weak_verb: Contains weak verbs/phrases

        Returns:
            Impact score (0-100)
        """
        score = 0

        if has_quantification:
            score += 40

        if has_strong_verb:
            score += 30
        elif not has_weak_verb:
            score += 10  # Neutral verb, some credit

        if is_concise:
            score += 20

        if is_active_voice:
            score += 10

        # Penalty for weak verbs
        if has_weak_verb:
            score = max(0, score - 20)

        return min(score, 100)

    def get_weakest_bullets(self, analyzed_bullets: List[Dict], count: int = 3) -> List[Dict]:
        """
        Get the weakest bullets from analyzed list.

        Args:
            analyzed_bullets: List of analyzed bullet dictionaries
            count: Number of weakest bullets to return

        Returns:
            List of weakest bullet analyses
        """
        # Sort by impact score (ascending)
        sorted_bullets = sorted(analyzed_bullets, key=lambda x: x['impact_score'])

        return sorted_bullets[:count]
