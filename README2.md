AI Resume Screening System
An AI-powered recruitment tool that helps HR teams quickly identify the most suitable candidates. HR uploads applicant resumes, pastes a job description, sets screening filters (minimum education, min/max experience, shortlist target), and gets a ranked shortlist of best-fit candidates.

Features
- Bulk Resume Upload: HR uploads multiple applicant resumes at once
- Job Description Matching: Paste a job description and screen resumes against it
- Configurable Filters: Set minimum education level, min/max years of experience, and shortlist size
- AI-Driven Scoring: Resumes are analyzed and ranked against the job requirements
- Shortlisting: Returns the top N candidates based on the configured shortlist target

Architecture
Resumes + Job Description + Filters (Frontend)
                    ↓
            Backend API (screening logic)
                    ↓
        AI/NLP Resume Analysis & Scoring
                    ↓
       Ranked Shortlist Returned to Frontend

Structure
- `backend/parser.py` — Extracts structured data (skills, education, experience) from uploaded resumes
- `backend/analyzer.py` — Scores/matches parsed resume data against the job description and filters
- `backend/app.py` — Backend entry point (likely the API/server that ties parser + analyzer together)
- `frontend/index` — HTML page for the HR-facing UI (upload, job description, filters)
- `frontend/style` — CSS styling for the UI
- `frontend/app` — Frontend logic (upload handling, calling the backend, rendering results)

> This is a plain HTML/CSS/JS frontend (no npm/React build step), not a JS framework app — corrected from my earlier assumption. One open question: is `frontend/app` a `.py` file (e.g. Flask serving `index.html`) or a `.js` file (client-side, calling the backend API directly)? That changes how it's run — check the actual extension and I'll adjust the run command.

📋 Prerequisites
- Python 3.x (for backend, and for frontend too if `app` is a `.py` file)
- A modern web browser (if `frontend/app` is plain client-side JS)
- An LLM/NLP provider API key, if `analyzer.py` calls an external model

🚀 Installation
1. Clone the repository
```
git clone https://github.com/mamoonali1/AI-Resume-Screening-System.git
cd AI-Resume-Screening-System
```

2. Set up the backend
```
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Set up the frontend
```
# If frontend/app is a Python file (Flask/similar):
cd ../frontend
pip install -r requirements.txt   # if a separate requirements file exists here

# If frontend/app is plain client-side JS, no install step is needed —
# it's served as a static file (see Usage below).
```

4. Configure environment variables
```
cp .env.example .env
# edit .env with your API keys / config
```


🎯 Usage
Start the backend
```
cd backend
python app.py
```

Start the frontend
```
cd frontend

# If frontend/app is a Python (Flask) file:
python app.py

# If frontend/app is plain client-side JS:
# just open index.html directly in a browser, or serve the folder with:
python -m http.server 5500
```

Then open the app in your browser, upload resumes, paste a job description, set your filters (minimum education, min/max experience, shortlist target), and run the screening.

📡 Example Workflow
1. HR uploads a batch of resumes (PDF/DOCX)
2. HR pastes the target job description
3. HR sets filters:
   - Minimum education (e.g., Bachelor's)
   - Minimum/maximum years of experience
   - Shortlist target (e.g., top 10)
4. The system scores each resume against the job description
5. The top-ranked candidates are returned as the shortlist


Project Structure
```
AI-Resume-Screening-System/
├── backend/
│   ├── app.py         # Backend entry point / API
│   ├── analyzer.py     # Resume-vs-job-description scoring & filtering logic
│   └── parser.py        # Resume parsing (extracts skills, education, experience)
├── frontend/
│   ├── app             # Frontend logic (confirm .py vs .js)
│   ├── index           # HTML page (confirm .html)
│   └── style           # CSS styling (confirm .css)
├── .gitignore
└── README.md
```
