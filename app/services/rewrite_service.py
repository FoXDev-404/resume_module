"""
AI-powered bullet point rewrite service using Gemini.
Rewrites weak bullet points with keyword injection and optimization.
"""

import logging
from typing import List, Dict
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import settings
from app.models.schemas import BulletRewrite

logger = logging.getLogger(__name__)


class RewriteService:
    """Service for AI-powered resume bullet rewriting."""

    def __init__(self):
        """Initialize Gemini model."""
        self.model = genai.GenerativeModel(settings.GEMINI_TEXT_MODEL)
        self.max_bullets_to_rewrite = settings.MAX_BULLETS_TO_REWRITE
        self.max_keywords_to_inject = settings.MAX_KEYWORDS_TO_INJECT

    async def rewrite_bullets(
        self,
        weak_bullets: List[Dict],
        missing_keywords: List[str],
        job_description: str
    ) -> List[Dict]:
        """
        Rewrite weak bullet points using AI.

        Args:
            weak_bullets: List of weak bullet analyses
            missing_keywords: Keywords from JD to incorporate
            job_description: Full job description for context

        Returns:
            List of bullet rewrites with originals and improvements
        """
        rewrites = []

        # Limit to top N weakest bullets
        bullets_to_rewrite = weak_bullets[:self.max_bullets_to_rewrite]

        # Limit keywords to inject
        keywords_to_use = missing_keywords[:self.max_keywords_to_inject]

        logger.info(f"Rewriting {len(bullets_to_rewrite)} bullets with {len(keywords_to_use)} keywords")

        for bullet_data in bullets_to_rewrite:
            original_text = bullet_data['text']
            original_score = bullet_data['impact_score']

            try:
                # Rewrite bullet
                rewritten = await self.rewrite_single_bullet(
                    bullet=original_text,
                    keywords=keywords_to_use,
                    job_description=job_description
                )

                # Determine keywords added
                keywords_added = self._identify_added_keywords(
                    original_text,
                    rewritten,
                    keywords_to_use
                )

                # Calculate improvement score
                improvement = 95 - original_score  # Assume rewrite hits ~95

                rewrites.append({
                    'original': original_text,
                    'rewritten': rewritten,
                    'improvement_score': max(0, improvement),
                    'keywords_added': keywords_added
                })

            except Exception as e:
                logger.error(f"Failed to rewrite bullet: {e}")
                # Skip this bullet if rewrite fails
                continue

        return rewrites

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def rewrite_single_bullet(
        self,
        bullet: str,
        keywords: List[str],
        job_description: str
    ) -> str:
        """
        Rewrite a single bullet point.

        Args:
            bullet: Original bullet text
            keywords: Keywords to incorporate
            job_description: Job description for context

        Returns:
            Rewritten bullet point

        Raises:
            Exception: If rewrite fails after retries
        """
        # Build prompt
        prompt = self._build_rewrite_prompt(bullet, keywords, job_description)

        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.7,
                    'max_output_tokens': 100,
                    'top_p': 0.95
                }
            )

            rewritten = response.text.strip()

            # Clean up response
            rewritten = self._clean_rewrite(rewritten)

            logger.debug(f"Rewrote bullet: '{bullet[:50]}...' -> '{rewritten[:50]}...'")
            return rewritten

        except Exception as e:
            logger.warning(f"Bullet rewrite failed: {e}")
            raise

    def _build_rewrite_prompt(
        self,
        bullet: str,
        keywords: List[str],
        job_description: str
    ) -> str:
        """
        Build prompt for bullet rewrite.

        Args:
            bullet: Original bullet
            keywords: Keywords to inject
            job_description: Job description

        Returns:
            Formatted prompt
        """
        # Truncate job description for context
        jd_context = job_description[:500]

        keywords_str = ", ".join(keywords[:3])  # Use top 3 keywords

        prompt = f"""You are an expert resume writer specializing in ATS optimization. Rewrite this resume bullet point to be more impactful.

Original bullet point:
"{bullet}"

Job description context:
{jd_context}

Keywords to naturally incorporate (use 1-2):
{keywords_str}

Requirements:
1. Start with a strong action verb (Led, Architected, Optimized, Increased, Reduced, Delivered, etc.)
2. Include 1-3 quantifiable metrics (numbers, percentages, dollar amounts)
3. Naturally weave in 1-2 of the missing keywords where appropriate
4. Keep it under 25 words
5. Maintain truthfulness - enhance the original, don't fabricate

Return ONLY the rewritten bullet point, no explanation, no quotes, no prefix."""

        return prompt

    def _clean_rewrite(self, text: str) -> str:
        """
        Clean up rewritten bullet text.

        Args:
            text: Raw rewrite output

        Returns:
            Cleaned bullet text
        """
        # Remove quotes if present
        text = text.strip('"').strip("'")

        # Remove any bullet markers
        text = text.lstrip('•●○■□▪▫-*').strip()

        # Remove common prefixes
        prefixes = [
            'Here is the rewritten bullet:',
            'Rewritten:',
            'Rewritten bullet:',
            'New bullet:',
            'Here you go:',
        ]

        for prefix in prefixes:
            if text.lower().startswith(prefix.lower()):
                text = text[len(prefix):].strip()
                text = text.lstrip(':').strip()

        # Capitalize first letter
        if text:
            text = text[0].upper() + text[1:]

        return text

    def _identify_added_keywords(
        self,
        original: str,
        rewritten: str,
        keywords: List[str]
    ) -> List[str]:
        """
        Identify which keywords were added in the rewrite.

        Args:
            original: Original bullet text
            rewritten: Rewritten bullet text
            keywords: List of candidate keywords

        Returns:
            List of keywords that were added
        """
        original_lower = original.lower()
        rewritten_lower = rewritten.lower()

        added = []

        for keyword in keywords:
            keyword_lower = keyword.lower()

            # Check if keyword is in rewritten but not in original
            if keyword_lower in rewritten_lower and keyword_lower not in original_lower:
                added.append(keyword)

        return added

    async def batch_rewrite(
        self,
        bullets: List[str],
        keywords: List[str],
        job_description: str
    ) -> List[str]:
        """
        Rewrite multiple bullets in batch.

        Args:
            bullets: List of bullet texts
            keywords: Keywords to incorporate
            job_description: Job description

        Returns:
            List of rewritten bullets
        """
        rewrites = []

        for bullet in bullets:
            try:
                rewritten = await self.rewrite_single_bullet(
                    bullet, keywords, job_description
                )
                rewrites.append(rewritten)
            except Exception as e:
                logger.error(f"Batch rewrite failed for bullet: {e}")
                # Keep original if rewrite fails
                rewrites.append(bullet)

        return rewrites
