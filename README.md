# resume-gen

`resume-gen` generates a tailored resume PDF for a job posting.

The project loads a base resume from `assets/data/resume_example.json`, scrapes a job posting URL, uses Gemini to extract the job requirements, rewrites the resume for that role, and renders the result with the LaTeX template in `assets/templates/resume_template.tex`. Generated files are written to `build/`.

## Requirements

- Python 3.12+
- uv
- A Google Gemini API key
- A working LaTeX/PDF toolchain for PDF rendering

## Setup

Install dependencies:

```bash
uv sync
```

Create a `.env` file in the project root:

```bash
GOOGLE_API_KEY=your_api_key_here
```

Add or update your source resume JSON at:

```bash
assets/data/resume_example.json
```

## Run

Generate a tailored resume from a job posting URL:

```bash
uv run python main.py "https://example.com/job-posting"
```

The generated PDF will be saved in `build/`.

## Project Layout

- `main.py` - command-line entry point
- `resume_pipeline.py` - end-to-end resume generation flow
- `resume_document.py` - resume loading, rendering, and PDF output
- `llm.py` - Gemini/LangChain calls for extraction, optimization, and compression
- `schema/` - Pydantic models for resume and job spec data
- `assets/prompts/` - prompts used by the LLM pipeline
- `assets/templates/` - LaTeX resume template
- `assets/schema/` - resume JSON schema
