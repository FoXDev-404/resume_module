"""
Embedding and semantic analysis service using Gemini API.
Handles semantic similarity computation and gap analysis.
"""

import json
import logging
from typing import Dict, List
import numpy as np
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for Gemini-powered semantic analysis."""

    def __init__(self):
        """Initialize Gemini models."""
        self.embedding_model = settings.GEMINI_EMBEDDING_MODEL
        self.text_model = genai.GenerativeModel(settings.GEMINI_TEXT_MODEL)

    async def compute_semantic_similarity(self, resume: str, job_description: str) -> float:
        """
        Compute semantic similarity between resume and job description.

        Args:
            resume: Resume text
            job_description: Job description text

        Returns:
            Semantic similarity score (0-100)
        """
        try:
            # Get embeddings for both texts
            resume_embedding = await self.get_embedding(resume)
            jd_embedding = await self.get_embedding(job_description)

            # Compute cosine similarity
            similarity = self.cosine_similarity(resume_embedding, jd_embedding)

            # Convert from [-1, 1] to [0, 100]
            score = ((similarity + 1) / 2) * 100

            logger.info(f"Semantic similarity score: {score:.2f}")
            return round(score, 2)

        except Exception as e:
            logger.error(f"Semantic similarity computation failed: {e}")
            # Return neutral score on failure
            return 50.0

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def get_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for text using Gemini.

        Args:
            text: Input text

        Returns:
            Embedding vector

        Raises:
            Exception: If embedding generation fails after retries
        """
        try:
            # Truncate text if too long (Gemini has token limits)
            text = text[:10000]

            result = genai.embed_content(
                model=self.embedding_model,
                content=text,
                task_type="retrieval_document"
            )

            embedding = result['embedding']
            logger.debug(f"Generated embedding with {len(embedding)} dimensions")
            return embedding

        except Exception as e:
            logger.warning(f"Embedding generation failed: {e}")
            raise

    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Cosine similarity (-1 to 1)
        """
        # Convert to numpy arrays
        v1 = np.array(vec1)
        v2 = np.array(vec2)

        # Calculate cosine similarity
        dot_product = np.dot(v1, v2)
        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)

        if norm_v1 == 0 or norm_v2 == 0:
            return 0.0

        similarity = dot_product / (norm_v1 * norm_v2)
        return float(similarity)

    async def analyze_semantic_gaps(self, resume: str, job_description: str) -> Dict:
        """
        Use Gemini to analyze semantic gaps between resume and job description.

        Args:
            resume: Resume text
            job_description: Job description text

        Returns:
            Dictionary with semantic score and identified gaps
        """
        try:
            # Create analysis prompt
            prompt = self._build_gap_analysis_prompt(resume, job_description)

            # Call Gemini
            response = await self._call_gemini_with_retry(prompt)

            # Parse response
            analysis = self._parse_gap_analysis(response)

            logger.info(f"Identified {len(analysis.get('gaps', []))} semantic gaps")
            return analysis

        except Exception as e:
            logger.error(f"Semantic gap analysis failed: {e}")
            return {
                'gaps': [],
                'explanation': 'Analysis unavailable'
            }

    def _build_gap_analysis_prompt(self, resume: str, job_description: str) -> str:
        """
        Build prompt for gap analysis.

        Args:
            resume: Resume text
            job_description: Job description text

        Returns:
            Formatted prompt
        """
        # Truncate for token limits
        resume_excerpt = resume[:3000]
        jd_excerpt = job_description[:2000]

        prompt = f"""Compare this resume with the job description and identify gaps.

Job Description:
{jd_excerpt}

Resume:
{resume_excerpt}

Analyze the semantic alignment and identify the top 3 most important skills, experiences, or qualifications mentioned in the job description that are missing or weakly represented in the resume.

Return your analysis as a JSON object with this structure:
{{
    "gaps": ["gap 1 description", "gap 2 description", "gap 3 description"]
}}

Be specific about what's missing. Focus on substantive gaps, not minor differences."""

        return prompt

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def _call_gemini_with_retry(self, prompt: str) -> str:
        """
        Call Gemini API with retry logic.

        Args:
            prompt: Prompt text

        Returns:
            Response text

        Raises:
            Exception: If call fails after retries
        """
        try:
            response = self.text_model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.7,
                    'max_output_tokens': 500
                }
            )

            return response.text

        except Exception as e:
            logger.warning(f"Gemini API call failed: {e}")
            raise

    def _parse_gap_analysis(self, response: str) -> Dict:
        """
        Parse gap analysis response from Gemini.

        Args:
            response: Raw response text

        Returns:
            Parsed analysis dictionary
        """
        try:
            # Try to extract JSON from response
            # Look for JSON block
            json_match = response.find('{')
            if json_match != -1:
                json_end = response.rfind('}')
                if json_end != -1:
                    json_str = response[json_match:json_end + 1]
                    analysis = json.loads(json_str)
                    return analysis

            # If no JSON found, try to parse as plain text
            logger.warning("Could not parse JSON response, using fallback")
            return {
                'gaps': [response.strip()]
            }

        except Exception as e:
            logger.error(f"Failed to parse gap analysis: {e}")
            return {
                'gaps': []
            }

    async def calculate_experience_alignment_score(
        self,
        gaps: List[str],
        semantic_score: float
    ) -> float:
        """
        Calculate experience alignment score based on gaps.

        Args:
            gaps: List of identified gaps
            semantic_score: Base semantic similarity score

        Returns:
            Experience alignment score (0-100)
        """
        # Start with semantic score
        score = semantic_score

        # Penalize based on number of gaps
        gap_penalty = len(gaps) * 10

        score = max(0, score - gap_penalty)

        return round(score, 2)
