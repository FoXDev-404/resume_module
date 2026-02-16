"""
FastAPI application - Main entry point for Resume Optimization SaaS.
Orchestrates all services to provide complete ATS analysis.
"""

import asyncio
import logging
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.models.schemas import AnalysisResponse
from app.services.parser_service import ParserService
from app.services.preprocess_service import PreprocessService
from app.services.keyword_service import KeywordService
from app.services.embedding_service import EmbeddingService
from app.services.impact_service import ImpactService
from app.services.rewrite_service import RewriteService
from app.services.scoring_service import ScoringService
from app.services.projection_service import ProjectionService
from app.utils.validators import validate_text_length

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.ENV == "production" else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Resume Optimization SaaS",
    description="AI-powered ATS resume optimization and scoring platform",
    version="1.0.0"
)

# CORS middleware (if needed for frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend/templates")

# Initialize services
parser_service = ParserService()
preprocess_service = PreprocessService()
keyword_service = KeywordService()
embedding_service = EmbeddingService()
impact_service = ImpactService()
rewrite_service = RewriteService()
scoring_service = ScoringService()
projection_service = ProjectionService()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Serve the frontend dashboard.

    Returns:
        HTML response with the main UI
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_resume(
    resume: Optional[UploadFile] = File(None),
    resume_text: Optional[str] = Form(None),
    job_description: str = Form(...)
):
    """
    Analyze resume against job description and provide comprehensive ATS scoring.

    This endpoint performs:
    1. Resume parsing (PDF or text)
    2. Keyword extraction and matching
    3. Semantic similarity analysis (Gemini)
    4. Bullet point impact analysis
    5. AI-powered rewrites for weak bullets
    6. Score projection after improvements

    Args:
        resume: Optional PDF file upload
        resume_text: Optional plain text resume
        job_description: Job description text (required)

    Returns:
        Complete analysis with scores, breakdowns, and recommendations

    Raises:
        HTTPException: If validation fails or processing errors occur
    """
    logger.info("Starting resume analysis")

    try:
        # Validate job description
        validate_text_length(
            job_description,
            min_length=settings.MIN_JD_LENGTH,
            max_length=settings.MAX_JD_LENGTH,
            field_name="Job description"
        )

        # Step 1: Parse resume
        logger.info("Step 1: Parsing resume")
        resume_content = await parser_service.parse_resume(
            file=resume,
            text=resume_text
        )

        # Step 2: Preprocess texts
        logger.info("Step 2: Preprocessing texts")
        clean_resume = preprocess_service.clean_text(resume_content)
        clean_jd = preprocess_service.normalize_job_description(job_description)
        resume_bullets = preprocess_service.extract_bullets(clean_resume)

        logger.info(f"Extracted {len(resume_bullets)} bullets from resume")

        # Step 3: Run parallel analyses
        logger.info("Step 3: Running parallel analyses")

        # These can run concurrently
        keyword_task = keyword_service.analyze_keywords(clean_jd, clean_resume, settings.TOP_KEYWORDS_COUNT)
        semantic_task = embedding_service.compute_semantic_similarity(clean_resume, clean_jd)
        impact_task = impact_service.analyze_all_bullets(resume_bullets)
        format_task = asyncio.create_task(
            asyncio.to_thread(parser_service.format_compliance_score, resume_content)
        )

        # Wait for all parallel tasks
        keyword_analysis, semantic_score, impact_analysis, format_score = await asyncio.gather(
            keyword_task,
            semantic_task,
            impact_task,
            format_task
        )

        logger.info("Parallel analyses complete")

        # Step 4: Calculate component scores
        logger.info("Step 4: Calculating score components")

        components = {
            'keyword_match': keyword_analysis['coverage_score'],
            'semantic_match': semantic_score,
            'impact_strength': impact_analysis['average_score'],
            'skills_alignment': keyword_analysis['skills_match_score'],
            'experience_alignment': semantic_score,  # Using semantic score as proxy
            'format_compliance': format_score
        }

        score_result = scoring_service.calculate_final_score(components)

        # Step 5: Identify weak bullets
        logger.info("Step 5: Identifying weak bullets")
        weak_bullets = impact_service.get_weakest_bullets(
            impact_analysis['bullets'],
            count=settings.MAX_BULLETS_TO_REWRITE
        )

        # Step 6: Generate rewrites using AI
        logger.info("Step 6: Generating AI rewrites")
        rewrites = await rewrite_service.rewrite_bullets(
            weak_bullets=weak_bullets,
            missing_keywords=keyword_analysis['missing_keywords'],
            job_description=clean_jd
        )

        logger.info(f"Generated {len(rewrites)} rewrites")

        # Step 7: Project improved score
        logger.info("Step 7: Projecting score improvements")
        projection = projection_service.project_improved_score(
            current_score=score_result['final_score'],
            current_breakdown=score_result['breakdown'],
            rewrites=rewrites,
            original_bullets=impact_analysis['bullets'],
            missing_keywords=keyword_analysis['missing_keywords'],
            total_keywords=settings.TOP_KEYWORDS_COUNT
        )

        # Step 8: Prepare response
        logger.info("Step 8: Preparing response")

        # Convert bullet analyses to Pydantic models
        weak_bullets_models = [
            {
                'text': b['text'],
                'impact_score': b['impact_score'],
                'has_quantification': b['has_quantification'],
                'weaknesses': b['weaknesses'],
                'strengths': b['strengths']
            }
            for b in weak_bullets
        ]

        response = AnalysisResponse(
            final_score=score_result['final_score'],
            breakdown=score_result['breakdown'],
            missing_keywords=keyword_analysis['missing_keywords'][:10],  # Top 10
            weak_bullets=weak_bullets_models,
            rewritten_bullets=rewrites,
            projected_score=projection['projected_score'],
            improvement_delta=projection['improvement']
        )

        logger.info(
            f"Analysis complete - Score: {response.final_score}, "
            f"Projected: {response.projected_score} (+{response.improvement_delta})"
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.

    Returns:
        Status dictionary
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.ENV
    }


@app.get("/api/info")
async def api_info():
    """
    Get API information.

    Returns:
        API metadata
    """
    return {
        "name": "Resume Optimization SaaS API",
        "version": "1.0.0",
        "description": "AI-powered ATS resume analysis and optimization",
        "endpoints": {
            "POST /analyze": "Analyze resume against job description",
            "GET /health": "Health check",
            "GET /": "Frontend dashboard"
        },
        "features": [
            "Multi-layer ATS scoring",
            "Keyword intelligence with TF-IDF",
            "Gemini-powered semantic analysis",
            "Impact strength analysis",
            "AI bullet point rewrites",
            "Score projection"
        ]
    }


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 errors."""
    return templates.TemplateResponse(
        "index.html",
        {"request": request},
        status_code=200  # Return homepage for any 404
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {exc}")
    return {"error": "Internal server error", "detail": "Please try again later"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENV != "production"
    )
