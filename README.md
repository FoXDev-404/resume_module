# Resume Optimization SaaS Platform

🚀 **AI-Powered ATS Resume Optimization and Scoring Engine**

A production-grade SaaS platform that analyzes resumes against job descriptions using multi-layer ATS simulation, semantic analysis, and AI-powered optimization. Built to compete with Jobscan and Teal.

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

---

## Features

### 🎯 Multi-Layer ATS Scoring Engine
- **6-component weighted scoring system:**
  - Keyword Match (30%) - TF-IDF-based keyword extraction
  - Semantic Match (25%) - Gemini embeddings + cosine similarity
  - Impact Strength (15%) - Bullet point analysis
  - Skills Alignment (10%) - Technical skills categorization
  - Experience Alignment (10%) - Semantic gap detection
  - Format Compliance (10%) - Structure and formatting checks

### 🤖 AI-Powered Intelligence
- **Gemini API Integration:**
  - Semantic similarity analysis
  - Experience gap identification
  - Automatic bullet point rewrites
  - Keyword injection with context awareness

### 📊 Comprehensive Analysis
- Keyword extraction and categorization (technical, soft skills, tools, certifications)
- Bullet point impact scoring (quantification, action verbs, conciseness)
- Missing keyword detection
- Score projection after applying optimizations

### 💻 Modern SaaS UI
- Clean, professional dashboard
- Animated score gauges
- Before/after bullet comparisons
- Progressive enhancement (works without JavaScript)
- Fully responsive design

---

## Architecture

```
resume_module/
├── app/
│   ├── config.py              # Environment & settings management
│   ├── main.py                # FastAPI application
│   ├── models/
│   │   └── schemas.py         # Pydantic data models
│   ├── services/              # Business logic layer
│   │   ├── parser_service.py
│   │   ├── preprocess_service.py
│   │   ├── keyword_service.py
│   │   ├── embedding_service.py
│   │   ├── impact_service.py
│   │   ├── rewrite_service.py
│   │   ├── scoring_service.py
│   │   └── projection_service.py
│   └── utils/
│       ├── text_utils.py
│       └── validators.py
├── frontend/
│   ├── templates/
│   │   └── index.html
│   └── static/
│       ├── styles.css
│       └── script.js
├── tests/                     # Pytest test suite
└── requirements.txt
```

---

## Tech Stack

- **Backend:** FastAPI (Python 3.11+)
- **AI/ML:** Google Generative AI (Gemini), scikit-learn
- **PDF Processing:** pdfplumber
- **Frontend:** Jinja2 templates + vanilla JavaScript
- **Testing:** pytest, pytest-asyncio
- **Deployment:** Vercel (@vercel/python)

---

## Installation

### Prerequisites
- Python 3.11 or higher
- Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

### Local Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd resume_module
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your Gemini API key:
   ```env
   GEMINI_API_KEY=your_actual_api_key_here
   ENV=development
   ```

5. **Download NLTK data (optional, for better keyword processing):**
   ```bash
   python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
   ```

---

## Usage

### Running Locally

1. **Start the development server:**
   ```bash
   uvicorn app.main:app --reload
   ```

2. **Access the application:**
   - Open browser to `http://localhost:8000`
   - Upload a resume (PDF or paste text)
   - Paste a job description
   - Click "Analyze Resume"
   - View comprehensive ATS analysis with AI-powered recommendations

### API Endpoints

#### `POST /analyze`
Analyze resume against job description.

**Request:**
```bash
curl -X POST http://localhost:8000/analyze \
  -F "resume=@resume.pdf" \
  -F "job_description=Your JD text here..."
```

**Response:**
```json
{
  "final_score": 76,
  "breakdown": {
    "keyword_match": {"score": 72, "weight": 30, "contribution": 21.6},
    "semantic_match": {"score": 85, "weight": 25, "contribution": 21.25},
    ...
  },
  "missing_keywords": ["Docker", "Kubernetes"],
  "weak_bullets": [...],
  "rewritten_bullets": [...],
  "projected_score": 84,
  "improvement_delta": 8
}
```

#### `GET /health`
Health check endpoint.

#### `GET /api/info`
API information and features.

---

## Testing

### Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_scoring_service.py -v

# Run only unit tests (skip integration)
pytest -m "not integration"
```

### Test Coverage
The test suite includes:
- Unit tests for all services
- Integration tests for API endpoints
- Mocked Gemini API calls (no actual API usage in tests)
- Edge case handling

---

## Deployment

### Deploy to Vercel

1. **Install Vercel CLI:**
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel:**
   ```bash
   vercel login
   ```

3. **Set environment variables:**
   ```bash
   vercel env add GEMINI_API_KEY
   ```
   Paste your Gemini API key when prompted.

4. **Deploy:**
   ```bash
   # Deploy preview
   vercel

   # Deploy to production
   vercel --prod
   ```

5. **Verify deployment:**
   - Open the provided URL
   - Check `/health` endpoint
   - Test analysis with sample resume

### Environment Variables (Production)

Required:
- `GEMINI_API_KEY` - Your Gemini API key

Optional:
- `MAX_RESUME_SIZE_MB` - Max upload size (default: 5)
- `TOP_KEYWORDS_COUNT` - Keywords to extract (default: 30)
- `ENV` - Environment (production/development)

---

## Configuration

### Scoring Weights

Customize scoring weights in `app/services/scoring_service.py`:

```python
self.weights = {
    'keyword_match': 0.30,          # 30%
    'semantic_match': 0.25,         # 25%
    'impact_strength': 0.15,        # 15%
    'skills_alignment': 0.10,       # 10%
    'experience_alignment': 0.10,   # 10%
    'format_compliance': 0.10       # 10%
}
```

### Bullet Scoring Criteria

Modify impact scoring in `app/services/impact_service.py`:
- Quantification: +40 points
- Strong action verb: +30 points
- Concise (<25 words): +20 points
- Active voice: +10 points
- Weak verb penalty: -20 points

---

## Troubleshooting

### Common Issues

**1. Gemini API Key Error:**
```
ValueError: GEMINI_API_KEY not configured
```
**Solution:** Ensure `.env` file exists with valid API key.

**2. PDF Parsing Fails:**
```
HTTPException: Could not extract text from PDF
```
**Solution:** PDF may be image-based. Use text paste instead.

**3. Module Import Errors:**
```
ModuleNotFoundError: No module named 'app'
```
**Solution:** Ensure you're running from project root and virtual environment is activated.

**4. Vercel Deployment Fails:**
**Solution:**
- Check `vercel.json` configuration
- Verify environment variables are set
- Check build logs for specific errors

### Performance Optimization

- **Caching:** Implement Redis for embedding caching in production
- **Rate Limiting:** Add rate limiting for public deployments
- **Async Processing:** All Gemini calls are async for better performance
- **Request Timeouts:** Configure timeout values in production

---

## Productionization Checklist

Before launching to production:

- [ ] Add authentication/authorization
- [ ] Implement rate limiting
- [ ] Set up monitoring (Sentry, DataDog)
- [ ] Add comprehensive logging
- [ ] Implement caching layer (Redis)
- [ ] Set up SSL/TLS
- [ ] Configure CORS appropriately
- [ ] Add database for analytics (optional)
- [ ] Implement error tracking
- [ ] Set up CI/CD pipeline
- [ ] Add backup strategy
- [ ] Configure auto-scaling
- [ ] Implement request validation limits
- [ ] Add API versioning

---

## API Limits & Costs

### Gemini API
- Free tier: Limited requests/day
- Pricing: Check [Google AI pricing](https://ai.google.dev/pricing)
- Each analysis makes 2-4 API calls:
  1. Resume embedding
  2. JD embedding
  3. Gap analysis (text generation)
  4. Bullet rewrites (3 requests)

**Cost optimization:**
- Cache embeddings for identical job descriptions
- Batch bullet rewrites when possible
- Use efficient prompt engineering

---

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Ensure tests pass: `pytest`
6. Submit a pull request

### Code Style
- Follow PEP 8
- Use type hints
- Add docstrings to all public functions
- Keep functions focused and testable

---

## License

MIT License - see LICENSE file for details

---

## Support

For issues, questions, or feedback:
- Open an issue on GitHub
- Check existing issues for solutions
- Review troubleshooting section above

---

## Roadmap

- [ ] Add resume builder integration
- [ ] Support for multiple resume formats (DOCX)
- [ ] LinkedIn profile import
- [ ] Industry-specific optimization
- [ ] Cover letter generation
- [ ] Interview question preparation
- [ ] Resume version comparison
- [ ] Chrome extension for one-click analysis
- [ ] Mobile app (React Native)

---

## Credits

Built with:
- [FastAPI](https://fastapi.tiangolo.com/)
- [Google Generative AI](https://ai.google.dev/)
- [scikit-learn](https://scikit-learn.org/)
- [pdfplumber](https://github.com/jsvine/pdfplumber)

---

**Made with ❤️ for job seekers everywhere**
