# SkillCart AI Backend Service

Production-grade AI Career Intelligence API backend service for the **SkillCart** platform. Built using **FastAPI**, **LangChain**, and **Pydantic v2**, with flexible support for **Google Gemini** and **Groq** APIs.

---

## Architecture Overview

The codebase is built following Clean Architecture principles:
- **`app/core/`**: Configuration, logging, exception rules.
- **`app/utils/`**: Core utilities, e.g. document parsers (PDF and DOCX).
- **`app/schemas/`**: Standard unified API JSON responses.
- **`app/ai/providers/`**: Pluggable LLM abstraction layer (Gemini, Groq).
- **`app/ai/prompts/`**: Prompt management decoupled from services logic.
- **`app/ai/models/`**: Pydantic validation structures for engine outputs.
- **`app/ai/services/`**: Core career engines logic.
- **`app/api/v1/`**: Routing and HTTP request handling.

---

## Career Engines Flow

```
Resume/File
    ↓ (Engine 1: Resume Intelligence)
Resume Schema JSON
    ↓ (Engine 2: Resume Evaluation & ATS Check)
ATS & Evaluation Report
    ↓ (Engine 3: Career Matching)
Job Matching Score & Skill Gaps
    ↓ (Engine 4: Career Enhancement)
Cover Letter, Learning Roadmap, Resume Flex
    ↓ (Engine 5: Interview Intelligence)
Tailored Interview Prep Q&A
    ↓ (Engine 6: Career Copilot)
Career Guidance Report & Chat Context
```

---

## Getting Started

### 1. Requirements
- Python 3.12+
- Gemini API Key and/or Groq API Key

### 2. Installation
Initialize virtual environment and install dependencies:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Environment Setup
Create a `.env` file from the example:
```bash
cp .env.example .env
```
Fill in your configuration and API keys:
- `GEMINI_API_KEY`: Google GenAI token.
- `GROQ_API_KEY`: Groq API token.
- `LLM_PROVIDER`: Set either `gemini` or `groq`.
- `RESUME_DATABASE_URL`: PostgreSQL URL used to fetch `resume.ai_response_json` by numeric `resume_id`.

### 4. Running Locally
Run the FastAPI development server:
```bash
uvicorn app.main:app --reload
```
Interactive Swagger API documentation is available at `http://localhost:8000/docs`.

---

## API Documentation

| Endpoint | Method | Input | Description |
| :--- | :--- | :--- | :--- |
| `/health` | `GET` | None | Service status check |
| `/api/v1/resume/parse` | `POST` | PDF/DOCX (Multipart) | Parse resume JSON without saving or generating a resume ID |
| `/api/v1/resume/generate` | `POST` | User-entered resume fields | Gemini-improved resume JSON with downloadable DOCX URL |
| `/api/v1/resume/{res_id}/download` | `GET` | Resume ID | Download generated or parsed resume as DOCX |
| `/api/v1/resume/evaluate` | `POST` | `EvaluateRequest` | Evaluation against standard & target JD |
| `/api/v1/career/match` | `POST` | `MatchRequest` | Scoring matching & gap analysis |
| `/api/v1/career/enhance` | `POST` | `EnhanceRequest` | Generates tailored resume, letter, & roadmap |
| `/api/v1/interview/prepare` | `POST` | `PrepareInterviewRequest` | Prepares interview prep Q&A |
| `/api/v1/copilot/guidance` | `POST` | `GuidanceRequest` | Generates holistic Guidance Report |
| `/api/v1/copilot/chat` | `POST` | `ChatRequest` | Conversational Career Copilot |

---

## Testing
Run the test suite:
```bash
pytest tests/
```
All tests use mock LLM provider invocations, meaning they can run offline without API tokens.
