"""
Pydantic models for request/response validation.
Provides type-safe contracts for all API interactions.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Optional


class ScoreBreakdown(BaseModel):
    """Individual component score in ATS analysis."""

    score: float = Field(..., ge=0, le=100, description="Component score (0-100)")
    weight: float = Field(..., ge=0, le=100, description="Weight percentage")
    contribution: float = Field(..., description="Weighted contribution to final score")


class BulletAnalysis(BaseModel):
    """Analysis of a single resume bullet point."""

    text: str = Field(..., description="Original bullet point text")
    impact_score: int = Field(..., ge=0, le=100, description="Impact strength score (0-100)")
    has_quantification: bool = Field(..., description="Whether bullet contains metrics")
    weaknesses: List[str] = Field(default_factory=list, description="Identified weaknesses")
    strengths: List[str] = Field(default_factory=list, description="Identified strengths")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Helped with testing",
                "impact_score": 25,
                "has_quantification": False,
                "weaknesses": ["weak verb: helped", "no metrics", "vague"],
                "strengths": []
            }
        }


class BulletRewrite(BaseModel):
    """AI-generated rewrite of a bullet point."""

    original: str = Field(..., description="Original bullet text")
    rewritten: str = Field(..., description="AI-optimized bullet text")
    improvement_score: int = Field(..., ge=0, le=100, description="Improvement points gained")
    keywords_added: List[str] = Field(default_factory=list, description="Keywords injected")

    class Config:
        json_schema_extra = {
            "example": {
                "original": "Helped with testing",
                "rewritten": "Executed 200+ automated test cases using Python, reducing bugs by 30%",
                "improvement_score": 70,
                "keywords_added": ["Python", "automated"]
            }
        }


class KeywordAnalysis(BaseModel):
    """Keyword extraction and matching results."""

    technical_skills: List[str] = Field(default_factory=list)
    soft_skills: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    domain_terms: List[str] = Field(default_factory=list)
    exact_matches: List[str] = Field(default_factory=list)
    partial_matches: List[str] = Field(default_factory=list)
    missing_keywords: List[str] = Field(default_factory=list)
    coverage_score: float = Field(..., ge=0, le=100)


class SemanticAnalysis(BaseModel):
    """Gemini-powered semantic similarity results."""

    semantic_score: float = Field(..., ge=0, le=100, description="Semantic alignment score")
    gaps: List[str] = Field(default_factory=list, description="Identified experience/skill gaps")


class AnalysisResponse(BaseModel):
    """Complete response from resume analysis."""

    final_score: int = Field(..., ge=0, le=100, description="Overall ATS score")
    breakdown: Dict[str, ScoreBreakdown] = Field(..., description="Score component breakdown")
    missing_keywords: List[str] = Field(..., description="Keywords from JD not in resume")
    weak_bullets: List[BulletAnalysis] = Field(..., description="Weakest bullet points")
    rewritten_bullets: List[BulletRewrite] = Field(..., description="AI-optimized rewrites")
    projected_score: int = Field(..., ge=0, le=100, description="Projected score after rewrites")
    improvement_delta: int = Field(..., description="Score improvement (projected - current)")

    class Config:
        json_schema_extra = {
            "example": {
                "final_score": 76,
                "breakdown": {
                    "keyword_match": {
                        "score": 72,
                        "weight": 30,
                        "contribution": 21.6
                    },
                    "semantic_match": {
                        "score": 85,
                        "weight": 25,
                        "contribution": 21.25
                    }
                },
                "missing_keywords": ["Docker", "Kubernetes", "Jenkins"],
                "weak_bullets": [
                    {
                        "text": "Helped with testing",
                        "impact_score": 25,
                        "has_quantification": False,
                        "weaknesses": ["weak verb: helped"],
                        "strengths": []
                    }
                ],
                "rewritten_bullets": [
                    {
                        "original": "Helped with testing",
                        "rewritten": "Executed 200+ automated test cases...",
                        "improvement_score": 70,
                        "keywords_added": ["Python"]
                    }
                ],
                "projected_score": 84,
                "improvement_delta": 8
            }
        }


class AnalyzeRequest(BaseModel):
    """Request payload for resume analysis."""

    job_description: str = Field(..., description="Job description text")

    @field_validator('job_description')
    @classmethod
    def validate_job_description(cls, v: str) -> str:
        """Validate job description length."""
        v = v.strip()
        if len(v) < 50:
            raise ValueError("Job description too short (minimum 50 characters)")
        if len(v) > 50000:
            raise ValueError("Job description too long (maximum 50,000 characters)")
        return v


class ProjectionResult(BaseModel):
    """Score projection after applying rewrites."""

    current_score: int = Field(..., ge=0, le=100)
    projected_score: int = Field(..., ge=0, le=100)
    improvement: int = Field(..., description="Absolute score increase")
    percentage_gain: float = Field(..., description="Percentage improvement")
    breakdown: Dict[str, float] = Field(default_factory=dict, description="Component improvements")
