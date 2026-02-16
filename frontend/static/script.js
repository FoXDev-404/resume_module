// Progressive Enhancement JavaScript for Resume Optimizer
// Works without JS, enhanced with AJAX when available

document.addEventListener('DOMContentLoaded', function () {
    // Element selectors
    const form = document.getElementById('analyzeForm');
    const fileInput = document.getElementById('resumeFile');
    const fileName = document.getElementById('fileName');
    const resumeText = document.getElementById('resumeText');
    const jobDescription = document.getElementById('jobDescription');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const analyzeAnotherBtn = document.getElementById('analyzeAnotherBtn');

    const uploadSection = document.getElementById('uploadSection');
    const loadingSection = document.getElementById('loadingSection');
    const resultsSection = document.getElementById('resultsSection');
    const loadingText = document.getElementById('loadingText');
    const progressFill = document.getElementById('progressFill');

    // File upload handler
    fileInput.addEventListener('change', function () {
        if (this.files.length > 0) {
            const file = this.files[0];
            fileName.textContent = file.name;

            // Clear text input if file is selected
            resumeText.value = '';

            // Validate file size (5MB)
            if (file.size > 5 * 1024 * 1024) {
                alert('File size must be less than 5MB');
                this.value = '';
                fileName.textContent = 'Choose PDF or TXT file (max 5MB)';
            }
        }
    });

    // Clear file input when text is entered
    resumeText.addEventListener('input', function () {
        if (this.value.trim()) {
            fileInput.value = '';
            fileName.textContent = 'Choose PDF or TXT file (max 5MB)';
        }
    });

    // Form submission
    form.addEventListener('submit', async function (e) {
        e.preventDefault();

        // Validation
        if (!fileInput.files.length && !resumeText.value.trim()) {
            alert('Please provide your resume (upload file or paste text)');
            return;
        }

        if (!jobDescription.value.trim()) {
            alert('Please paste the job description');
            return;
        }

        if (jobDescription.value.trim().length < 50) {
            alert('Job description is too short (minimum 50 characters)');
            return;
        }

        // Show loading state
        uploadSection.classList.add('hidden');
        loadingSection.classList.remove('hidden');
        resultsSection.classList.add('hidden');

        // Simulate progress (visual feedback)
        simulateProgress();

        // Prepare form data
        const formData = new FormData();

        if (fileInput.files.length > 0) {
            formData.append('resume', fileInput.files[0]);
        } else {
            formData.append('resume_text', resumeText.value.trim());
        }

        formData.append('job_description', jobDescription.value.trim());

        try {
            // Make API request
            const response = await fetch('/analyze', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Analysis failed');
            }

            const data = await response.json();

            // Display results
            displayResults(data);

        } catch (error) {
            console.error('Error:', error);
            alert('Analysis failed: ' + error.message);

            // Reset to upload section
            loadingSection.classList.add('hidden');
            uploadSection.classList.remove('hidden');
        }
    });

    // Analyze another button
    analyzeAnotherBtn.addEventListener('click', function () {
        // Reset form
        form.reset();
        fileName.textContent = 'Choose PDF or TXT file (max 5MB)';

        // Show upload section
        resultsSection.classList.add('hidden');
        uploadSection.classList.remove('hidden');

        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    // Simulate progress bar
    function simulateProgress() {
        let progress = 0;
        const messages = [
            'Parsing resume...',
            'Analyzing keywords...',
            'Computing semantic match...',
            'Analyzing bullet points...',
            'Generating AI rewrites...',
            'Calculating scores...'
        ];

        const interval = setInterval(() => {
            progress += Math.random() * 15;

            if (progress >= 100) {
                progress = 100;
                clearInterval(interval);
            }

            progressFill.style.width = progress + '%';

            // Update message
            const messageIndex = Math.min(Math.floor(progress / 20), messages.length - 1);
            loadingText.textContent = messages[messageIndex];
        }, 500);
    }

    // Display results
    function displayResults(data) {
        // Hide loading, show results
        loadingSection.classList.add('hidden');
        resultsSection.classList.remove('hidden');

        // Animate score gauge
        animateScore(data.final_score, data.projected_score, data.improvement_delta);

        // Populate breakdown
        populateBreakdown(data.breakdown);

        // Populate missing keywords
        populateKeywords(data.missing_keywords);

        // Populate rewrites
        populateRewrites(data.rewritten_bullets);

        // Populate projection summary
        populateProjection(data.final_score, data.projected_score, data.improvement_delta);

        // Scroll to results
        setTimeout(() => {
            resultsSection.scrollIntoView({ behavior: 'smooth' });
        }, 100);
    }

    // Animate score gauge
    function animateScore(current, projected, improvement) {
        const currentScoreEl = document.getElementById('currentScore');
        const projectedScoreEl = document.getElementById('projectedScore');
        const improvementEl = document.getElementById('improvement');
        const scoreCircle = document.getElementById('scoreCircle');

        // Animate current score
        animateNumber(currentScoreEl, 0, current, 1500);

        // Animate projected score
        setTimeout(() => {
            animateNumber(projectedScoreEl, 0, projected, 1500);
        }, 250);

        // Show improvement
        improvementEl.textContent = improvement >= 0 ? `+${improvement}` : improvement;

        // Animate circle
        const circumference = 565;
        const offset = circumference - (current / 100) * circumference;
        scoreCircle.style.strokeDashoffset = offset;
    }

    // Animate number counting
    function animateNumber(element, start, end, duration) {
        const range = end - start;
        const increment = range / (duration / 16);
        let current = start;

        const timer = setInterval(() => {
            current += increment;
            if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
                current = end;
                clearInterval(timer);
            }
            element.textContent = Math.round(current);
        }, 16);
    }

    // Populate breakdown cards
    function populateBreakdown(breakdown) {
        const breakdownGrid = document.getElementById('breakdownGrid');
        breakdownGrid.innerHTML = '';

        const labels = {
            keyword_match: 'Keyword Match',
            semantic_match: 'Semantic Match',
            impact_strength: 'Impact Strength',
            skills_alignment: 'Skills Alignment',
            experience_alignment: 'Experience Alignment',
            format_compliance: 'Format Compliance'
        };

        for (const [key, data] of Object.entries(breakdown)) {
            const card = document.createElement('div');
            card.className = 'breakdown-card';
            card.innerHTML = `
                <div class="breakdown-card-title">${labels[key] || key}</div>
                <div class="breakdown-card-score">${Math.round(data.score)}</div>
                <div class="breakdown-card-weight">${data.weight}% weight</div>
            `;
            breakdownGrid.appendChild(card);
        }
    }

    // Populate missing keywords
    function populateKeywords(keywords) {
        const keywordsContainer = document.getElementById('keywordsContainer');
        keywordsContainer.innerHTML = '';

        if (keywords.length === 0) {
            keywordsContainer.innerHTML = '<p style="color: var(--secondary);">All major keywords are present in your resume!</p>';
            return;
        }

        keywords.forEach(keyword => {
            const chip = document.createElement('span');
            chip.className = 'keyword-chip';
            chip.textContent = keyword;
            keywordsContainer.appendChild(chip);
        });
    }

    // Populate rewrites
    function populateRewrites(rewrites) {
        const rewritesContainer = document.getElementById('rewritesContainer');
        rewritesContainer.innerHTML = '';

        if (rewrites.length === 0) {
            rewritesContainer.innerHTML = '<p>No rewrites needed - your bullets are already strong!</p>';
            return;
        }

        rewrites.forEach((rewrite, index) => {
            const card = document.createElement('div');
            card.className = 'rewrite-card';

            const keywordsAdded = rewrite.keywords_added.length > 0
                ? `<div class="keywords-added"><strong>Keywords added:</strong> ${rewrite.keywords_added.join(', ')}</div>`
                : '';

            card.innerHTML = `
                <div class="rewrite-header">
                    <span class="rewrite-number">Improvement #${index + 1}</span>
                    <span class="improvement-badge">+${rewrite.improvement_score} points</span>
                </div>
                <div class="bullet-comparison">
                    <div class="bullet-item bullet-original">
                        <div class="bullet-label">❌ Original</div>
                        <div class="bullet-text">${escapeHtml(rewrite.original)}</div>
                    </div>
                    <div class="bullet-item bullet-rewritten">
                        <div class="bullet-label">✅ Optimized</div>
                        <div class="bullet-text">${escapeHtml(rewrite.rewritten)}</div>
                        ${keywordsAdded}
                    </div>
                </div>
            `;
            rewritesContainer.appendChild(card);
        });
    }

    // Populate projection summary
    function populateProjection(current, projected, improvement) {
        const summaryEl = document.getElementById('projectionSummary');

        const percentage = ((improvement / current) * 100).toFixed(1);

        summaryEl.innerHTML = `
            Applying these changes will improve your ATS score from
            <strong>${current}</strong> to <strong>${projected}</strong>
            (<strong>+${improvement} points, ${percentage}% increase</strong>).
            This significantly increases your chances of passing automated screening.
        `;
    }

    // Utility: Escape HTML
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
});
