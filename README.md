# Career Assistant

An AI-powered tool that helps job seekers optimize their CV and cover letters for ATS systems.

## Features

- CV Analysis & ATS Score
- Job Description Matching
- CV Optimization Suggestions
- Automatic Cover Letter Generation

## Quick Start

```bash
# Clone repository
git clone https://github.com/baccourihazem/Career-Assistant.git
cd Career-Assistant

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run ui/streamlit_app.py
```

## Requirements

- Python 3.8+
- Streamlit
- OpenAI API key

## Usage

1. Upload your CV (PDF/DOCX)
2. Paste job description
3. Click "Start Analysis"
4. View results in different tabs:
   - ATS Score
   - Match Analysis
   - Optimization Tips
   - Cover Letter

## Project Structure

```
Career-Assistant/
├── agents/          # Core analysis modules
├── models/          # AI model handlers
├── utils/           # Helper functions
├── ui/              # Streamlit interface
└── tests/           # Unit & E2E tests
```

## Contact

Hazem EL BACCOURI - baccouri.hamza@gmail.com
