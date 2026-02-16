"""
Keyword extraction and matching service using TF-IDF.
Handles keyword categorization, matching, and coverage scoring.
"""

import re
import logging
from typing import Dict, List, Set
from sklearn.feature_extraction.text import TfidfVectorizer
from app.utils.text_utils import lemmatize_word

logger = logging.getLogger(__name__)


class KeywordService:
    """Service for extracting and matching keywords from job descriptions."""

    def __init__(self):
        """Initialize keyword service with categorization dictionaries."""
        # Technical skills keywords
        self.technical_skills = {
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'go', 'rust',
            'php', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'sql', 'nosql', 'html', 'css',
            'react', 'angular', 'vue', 'node', 'django', 'flask', 'spring', 'express',
            'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy',
            'machine learning', 'deep learning', 'ai', 'artificial intelligence',
            'data science', 'nlp', 'computer vision', 'neural networks'
        }

        # Soft skills keywords
        self.soft_skills = {
            'leadership', 'communication', 'teamwork', 'collaboration', 'problem-solving',
            'critical thinking', 'analytical', 'creative', 'adaptable', 'flexible',
            'time management', 'organizational', 'detail-oriented', 'self-motivated',
            'initiative', 'presentation', 'interpersonal', 'mentoring', 'coaching'
        }

        # Tools and technologies
        self.tools = {
            'git', 'github', 'gitlab', 'bitbucket', 'jira', 'confluence', 'slack',
            'docker', 'kubernetes', 'jenkins', 'circleci', 'travis', 'terraform',
            'ansible', 'puppet', 'chef', 'aws', 'azure', 'gcp', 'heroku', 'vercel',
            'linux', 'unix', 'windows', 'macos', 'bash', 'powershell',
            'vscode', 'intellij', 'eclipse', 'pycharm', 'jupyter'
        }

        # Certifications
        self.certifications = {
            'aws certified', 'azure certified', 'gcp certified', 'pmp', 'scrum master',
            'cissp', 'comptia', 'ceh', 'cisa', 'cism', 'itil', 'ccna', 'ccnp',
            'certified kubernetes', 'tableau certified', '', 'cfa', 'six sigma'
        }

    async def analyze_keywords(self, job_description: str, resume: str, top_n: int = 30) -> Dict:
        """
        Analyze keywords in job description and match against resume.

        Args:
            job_description: Job description text
            resume: Resume text
            top_n: Number of top keywords to extract

        Returns:
            Dictionary with categorized keywords, matches, and coverage score
        """
        # Extract keywords from job description
        jd_keywords = self.extract_keywords(job_description, top_n=top_n)

        # Categorize keywords
        categorized = self.categorize_keywords(jd_keywords)

        # Match against resume
        matches = self.match_keywords(resume, jd_keywords)

        # Calculate scores
        coverage_score = self.calculate_coverage_score(
            len(matches['exact']) + len(matches['partial']) * 0.5,
            len(jd_keywords)
        )

        skills_match_score = self.calculate_skills_match_score(resume, categorized)

        return {
            'keywords': categorized,
            'exact_matches': matches['exact'],
            'partial_matches': matches['partial'],
            'missing_keywords': matches['missing'],
            'coverage_score': coverage_score,
            'skills_match_score': skills_match_score
        }

    def extract_keywords(self, text: str, top_n: int = 30) -> List[str]:
        """
        Extract top keywords using TF-IDF.

        Args:
            text: Input text
            top_n: Number of keywords to extract

        Returns:
            List of top keywords
        """
        try:
            # Create TF-IDF vectorizer
            vectorizer = TfidfVectorizer(
                max_features=top_n * 2,  # Get extra to filter later
                stop_words='english',
                ngram_range=(1, 3),  # Unigrams, bigrams, trigrams
                min_df=1,
                max_df=0.95
            )

            # Fit and transform
            tfidf_matrix = vectorizer.fit_transform([text])
            feature_names = vectorizer.get_feature_names_out()

            # Get scores
            scores = tfidf_matrix.toarray()[0]

            # Sort by score
            keyword_scores = list(zip(feature_names, scores))
            keyword_scores.sort(key=lambda x: x[1], reverse=True)

            # Extract top keywords
            keywords = [kw for kw, score in keyword_scores[:top_n] if score > 0]

            # Filter out very short keywords (< 2 chars)
            keywords = [kw for kw in keywords if len(kw) >= 2]

            logger.info(f"Extracted {len(keywords)} keywords from text")
            return keywords

        except Exception as e:
            logger.error(f"Keyword extraction failed: {e}")
            # Fallback to simple word frequency
            return self._simple_keyword_extraction(text, top_n)

    def _simple_keyword_extraction(self, text: str, top_n: int) -> List[str]:
        """
        Simple fallback keyword extraction using word frequency.

        Args:
            text: Input text
            top_n: Number of keywords

        Returns:
            List of keywords
        """
        # Convert to lowercase
        text = text.lower()

        # Remove punctuation
        text = re.sub(r'[^\w\s]', ' ', text)

        # Split into words
        words = text.split()

        # Count frequencies
        freq = {}
        for word in words:
            if len(word) > 2:  # Skip very short words
                freq[word] = freq.get(word, 0) + 1

        # Sort by frequency
        sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)

        return [word for word, count in sorted_words[:top_n]]

    def categorize_keywords(self, keywords: List[str]) -> Dict[str, List[str]]:
        """
        Categorize keywords into technical skills, soft skills, tools, etc.

        Args:
            keywords: List of keywords

        Returns:
            Dictionary with categorized keywords
        """
        categorized = {
            'technical_skills': [],
            'soft_skills': [],
            'tools': [],
            'certifications': [],
            'domain_terms': []
        }

        for keyword in keywords:
            keyword_lower = keyword.lower()
            categorized_flag = False

            # Check technical skills
            if any(skill in keyword_lower for skill in self.technical_skills):
                categorized['technical_skills'].append(keyword)
                categorized_flag = True

            # Check soft skills
            if any(skill in keyword_lower for skill in self.soft_skills):
                categorized['soft_skills'].append(keyword)
                categorized_flag = True

            # Check tools
            if any(tool in keyword_lower for tool in self.tools):
                categorized['tools'].append(keyword)
                categorized_flag = True

            # Check certifications
            if any(cert in keyword_lower for cert in self.certifications):
                categorized['certifications'].append(keyword)
                categorized_flag = True

            # If not categorized, add to domain terms
            if not categorized_flag:
                categorized['domain_terms'].append(keyword)

        return categorized

    def match_keywords(self, resume: str, keywords: List[str]) -> Dict[str, List[str]]:
        """
        Match keywords against resume text.

        Args:
            resume: Resume text
            keywords: List of keywords to match

        Returns:
            Dictionary with exact, partial, and missing matches
        """
        resume_lower = resume.lower()
        exact_matches = []
        partial_matches = []
        missing = []

        for keyword in keywords:
            keyword_lower = keyword.lower()

            # Check for exact match
            if re.search(r'\b' + re.escape(keyword_lower) + r'\b', resume_lower):
                exact_matches.append(keyword)
            # Check for partial match using lemmatization
            elif self._check_partial_match(keyword_lower, resume_lower):
                partial_matches.append(keyword)
            else:
                missing.append(keyword)

        logger.info(f"Matched {len(exact_matches)} exact, {len(partial_matches)} partial, {len(missing)} missing")
        return {
            'exact': exact_matches,
            'partial': partial_matches,
            'missing': missing
        }

    def _check_partial_match(self, keyword: str, text: str) -> bool:
        """
        Check for partial keyword match using lemmatization.

        Args:
            keyword: Keyword to find
            text: Text to search in

        Returns:
            True if partial match found
        """
        # Lemmatize keyword
        keyword_lemma = lemmatize_word(keyword)

        # Check if lemmatized form exists in text
        return keyword_lemma in text

    def calculate_coverage_score(self, matched_count: float, total_count: int) -> float:
        """
        Calculate keyword coverage score.

        Args:
            matched_count: Number of matched keywords (can be fractional for partial matches)
            total_count: Total number of keywords

        Returns:
            Coverage score (0-100)
        """
        if total_count == 0:
            return 0.0

        score = (matched_count / total_count) * 100
        return round(min(score, 100.0), 2)

    def calculate_skills_match_score(self, resume: str, categorized: Dict[str, List[str]]) -> float:
        """
        Calculate specialized score for technical skills matching.

        Args:
            resume: Resume text
            categorized: Categorized keywords

        Returns:
            Skills match score (0-100)
        """
        # Focus on technical skills for this score
        technical_skills = categorized.get('technical_skills', [])

        if not technical_skills:
            return 50.0  # Neutral score if no technical skills in JD

        resume_lower = resume.lower()
        matched = sum(1 for skill in technical_skills if skill.lower() in resume_lower)

        score = (matched / len(technical_skills)) * 100
        return round(min(score, 100.0), 2)
