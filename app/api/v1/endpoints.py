from typing import Optional, List
import anyio
import json
import requests

# pyrefly: ignore [missing-import]
from fastapi import APIRouter, File, UploadFile, Depends, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from io import BytesIO
from urllib.parse import urlparse
import requests
import os

from app.schemas.api_response import ApiResponse, success_response
from app.ai.services.models import (
    CertificationItem,
    ContactDetails,
    EducationItem,
    ExperienceItem,
    ProjectItem,
    ResumeSchema,
    ResumeEvaluationSchema,
    CareerMatchSchema,
    CareerEnhancementSchema,
    InterviewPrepSchema,
    CareerGuidanceReportSchema,
    SkillCategory,
    ChatResponseSchema,
    ChatMessage,
    ChatRequest,
    ResumeAnalysisReportSchema,
    GenResumeSchema,
)
from app.ai.services.resume_intel import ResumeIntelligenceService
from app.ai.services.resume_generate import ResumeGenerationService
from app.ai.services.resume_eval import ResumeEvaluationService
from app.ai.services.career_match import CareerMatchingService
from app.ai.services.career_enhance import CareerEnhancementService
from app.ai.services.interview import InterviewIntelligenceService
from app.ai.services.copilot import CareerCopilotService
from app.ai.services.resume_analyze import ResumeAnalysisService
from app.utils.document_parsers import extract_text_from_file
from app.utils.resume_export import build_gen_resume_docx
from app.core.db import save_resume_data, get_resume_data
from app.core.exceptions import SkillCartException
from app.core.railway_client import railway_client
from app.core.resume_ai_db import get_resume_ai_response_data

router = APIRouter()

# =====================================================================
# Helper to Resolve Resume (Database Lookup)
# =====================================================================


def resolve_resume(res_id: str) -> ResumeSchema:
    """Resolve ResumeSchema from database res_id."""
    if not res_id:
        raise SkillCartException(message="'res_id' must be provided.", status_code=400)

    is_numeric_resume_id = str(res_id).strip().isdigit()
    try:
        data = get_resume_ai_response_data(res_id)
    except ValueError as e:
        raise SkillCartException(
            message="Resume AI database is not configured.",
            status_code=500,
            errors=str(e),
        )
    except Exception as e:
        raise SkillCartException(
            message=f"Failed to fetch resume AI data for ID '{res_id}'.",
            status_code=502,
            errors=str(e),
        )

    if data is None and not is_numeric_resume_id:
        data = get_resume_data(res_id)

    if not data:
        raise SkillCartException(
            message=f"Resume with ID '{res_id}' not found in the database.",
            status_code=404,
        )
    try:
        return ResumeSchema(**data)
    except Exception as e:
        raise SkillCartException(
            message=f"Failed to parse database resume data for ID '{res_id}': {str(e)}",
            status_code=422,
        )


def resolve_generated_resume(res_id: str) -> GenResumeSchema:
    """Resolve GenResumeSchema from database res_id."""
    if not res_id:
        raise SkillCartException(message="'res_id' must be provided.", status_code=400)

    is_numeric_resume_id = str(res_id).strip().isdigit()
    try:
        data = get_resume_ai_response_data(res_id)
    except ValueError as e:
        raise SkillCartException(
            message="Resume AI database is not configured.",
            status_code=500,
            errors=str(e),
        )
    except Exception as e:
        raise SkillCartException(
            message=f"Failed to fetch resume AI data for ID '{res_id}'.",
            status_code=502,
            errors=str(e),
        )

    if data is None and not is_numeric_resume_id:
        data = get_resume_data(res_id)

    if not data:
        raise SkillCartException(
            message=f"Resume with ID '{res_id}' not found in the database.",
            status_code=404,
        )
    try:
        return GenResumeSchema(**data)
    except Exception as e:
        raise SkillCartException(
            message=f"Failed to parse database resume data for ID '{res_id}': {str(e)}",
            status_code=422,
        )


# =====================================================================
# Request Schemas for APIs
# =====================================================================
class ResumeParseRequest(BaseModel):
    file_bytes: bytes


class EvaluateRequest(BaseModel):
    res_id: str
    job_id: str


class MatchRequest(BaseModel):
    res_id: str
    top_k: int = 10


class EnhanceRequest(BaseModel):
    res_id: str
    match_report: CareerMatchSchema


class PrepareInterviewRequest(BaseModel):
    res_id: Optional[str]
    job_id: str
    category: str = Field(..., description="Category: 'Technical', 'HR', 'Behavioral', 'Coding', 'Company'")


class GuidanceRequest(BaseModel):
    res_id: str
    evaluation: ResumeEvaluationSchema
    match: CareerMatchSchema


def _resume_download_filename(name: str) -> str:
    cleaned = "".join(
        char.lower() if char.isalnum() else "-" for char in (name or "resume")
    ).strip("-")

    while "--" in cleaned:
        cleaned = cleaned.replace("--", "-")

    return f"{cleaned or 'resume'}-resume.docx"


def _format_job_list(title: str, items: Optional[List[str]]) -> Optional[str]:
    values = [str(item).strip() for item in items or [] if str(item).strip()]
    if not values:
        return None
    return f"{title}: " + ", ".join(values)


def _is_parse_resume_like_text(raw_text: str) -> bool:
    text = (raw_text or "").lower()
    if len(text.strip()) < 30:
        return False

    signals = [
        "resume",
        "curriculum vitae",
        "education",
        "experience",
        "work experience",
        "skills",
        "projects",
        "certification",
        "certifications",
        "linkedin",
        "github",
        "portfolio",
        "degree",
        "university",
        "college",
        "intern",
        "developer",
        "engineer",
    ]
    return sum(1 for signal in signals if signal in text) >= 2


def _has_parse_resume_structure(resume: ResumeSchema) -> bool:
    name = (resume.name or "").strip().lower()
    if not name or name in {"unknown", "not provided", "n/a", "none"}:
        return False

    contact_values = [
        resume.contact.email,
        resume.contact.phone,
        resume.contact.location,
        resume.contact.linkedin,
        resume.contact.github,
        resume.contact.portfolio,
    ]
    contact_count = sum(1 for value in contact_values if value)
    section_count = sum(
        1
        for section in [
            resume.education,
            resume.experience,
            resume.projects,
            resume.skills,
            resume.certifications,
        ]
        if section
    )

    return section_count >= 1 and (contact_count >= 1 or section_count >= 2)


def _build_job_description(job: dict) -> str:
    company = job.get("company") or {}
    experience_min = job.get("experience_min")
    experience_max = job.get("experience_max")

    lines = [
        f"Job Title: {job['job_title']}" if job.get("job_title") else None,
        f"Company: {company['company_name']}" if company.get("company_name") else None,
        f"Department: {job['department']}" if job.get("department") else None,
        f"Project Role: {job['project_role']}" if job.get("project_role") else None,
        (
            f"Employment Type: {job['employment_type']}"
            if job.get("employment_type")
            else None
        ),
        f"Work Mode: {job['work_mode']}" if job.get("work_mode") else None,
        f"Location: {job['location']}" if job.get("location") else None,
        (
            f"Experience Required: {experience_min}-{experience_max} years"
            if experience_min is not None and experience_max is not None
            else (
                f"Minimum Experience Required: {experience_min} years"
                if experience_min is not None
                else (
                    f"Maximum Experience Allowed: {experience_max} years"
                    if experience_max is not None
                    else None
                )
            )
        ),
        f"Education Requirement: {job['education']}" if job.get("education") else None,
        f"Role Summary: {job['summary']}" if job.get("summary") else None,
        (
            f"Role Description: {job['project_role_description']}"
            if job.get("project_role_description")
            else None
        ),
        (
            f"Company Overview: {company['description']}"
            if company.get("description")
            else None
        ),
        (
            f"Additional Information: {job['additional_information']}"
            if job.get("additional_information")
            else None
        ),
        _format_job_list("Responsibilities", job.get("responsibilities")),
        _format_job_list("Required Skills", job.get("required_skills")),
        _format_job_list("Preferred Skills", job.get("preferred_skills")),
        _format_job_list("Professional Skills", job.get("professional_skills")),
    ]
    return "\n".join(line for line in lines if line)


# =====================================================================
# Endpoints
# =====================================================================


@router.post("/resume/parse", response_model=ApiResponse)
async def parse_resume_endpoint(request: Request):

    # Receive raw PDF/DOCX bytes
    file_bytes = await request.body()

    if not file_bytes:
        return success_response(message="No resume bytes received.", data=None)

    # Detect file type from bytes
    if file_bytes.startswith(b"%PDF"):
        filename = "resume.pdf"
    elif file_bytes.startswith(b"PK"):
        # DOCX is a ZIP-based file
        filename = "resume.docx"
    else:
        return success_response(
            message="Unsupported or invalid resume file.", data=None
        )

    # Extract text
    raw_text = extract_text_from_file(filename, file_bytes)

    if not _is_parse_resume_like_text(raw_text):
        return success_response(
            message="Uploaded file does not appear to be a resume.", data=None
        )

    # Gemini parsing
    result = await ResumeIntelligenceService.parse_resume(raw_text)

    if not _has_parse_resume_structure(result):
        return success_response(
            message="Uploaded file does not appear to be a resume.", data=None
        )

    return success_response(data=result.model_dump(mode="json"))


@router.post("/resume/generate", response_model=ApiResponse)
async def generate_resume_endpoint(req: ResumeSchema, request: Request):
    """Generate a structured resume from user-entered fields and save it."""
    name = req.name.strip()
    if not name:
        raise SkillCartException(message="'name' must be provided.", status_code=400)

    draft_resume = req.model_copy(update={"name": name})
    resume = await ResumeGenerationService.improve_gen_resume(draft_resume)
    parsed_dict = resume.model_dump(mode="json")

    save_resume_data(
        res_id=str(resume.res_id),
        name=resume.name,
        raw_text=json.dumps(parsed_dict, indent=2),
        parsed_data=parsed_dict,
    )

    download_url = str(
        request.url_for("download_resume_endpoint", res_id=str(resume.res_id))
    )

    return success_response(
        data={
            "res_id": str(resume.res_id),
            "parsed_data": parsed_dict,
            "resume": parsed_dict,
            "download_url": download_url,
        },
        message="Resume generated successfully",
    )


@router.get("/resume/{res_id}/download")
async def download_resume_endpoint(res_id: str):
    """Download a stored resume as a DOCX document."""
    resume = resolve_generated_resume(res_id)
    document_bytes = await anyio.to_thread.run_sync(build_gen_resume_docx, resume)
    filename = _resume_download_filename(resume.name)

    return StreamingResponse(
        BytesIO(document_bytes),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/resume/{res_id}", response_model=ApiResponse)
async def get_resume_data_endpoint(res_id: str):
    """Retrieve the extracted parsed resume data from the database by resume ID."""
    data = get_resume_ai_response_data(res_id)
    if not data:
        raise SkillCartException(
            message=f"Resume with ID '{res_id}' not found in the database.",
            status_code=404
        )
        
    return success_response(
        data=data,
        message="Parsed resume data retrieved successfully"
    )


@router.post("/resume/analyze", response_model=ApiResponse)
async def analyze_resume_endpoint(file: UploadFile = File(...)):
    """Upload a PDF/DOCX resume file, parse it, and perform custom Resume Analysis strictly on its content."""
    file_bytes = await file.read()
    raw_text = extract_text_from_file(file.filename, file_bytes)
    resume = await ResumeIntelligenceService.parse_resume(raw_text)

    # Perform detailed analysis strictly on resume content
    analysis = await ResumeAnalysisService.analyze_resume(resume)

    return success_response(data=analysis, message="Resume analyzed successfully")


@router.post("/resume/evaluate", response_model=ApiResponse)
async def evaluate_resume_endpoint(req: EvaluateRequest):
    """Evaluate a parsed resume against a target job fetched by job ID."""
    resume = resolve_resume(req.res_id)
    try:
        job_id = int(req.job_id.strip())
    except ValueError:
        raise SkillCartException(
            message="'job_id' must be a valid integer.", status_code=400
        )

    try:
        job = await anyio.to_thread.run_sync(railway_client.get_job, job_id)
    except requests.HTTPError as exc:
        if exc.response is not None and exc.response.status_code == 404:
            raise SkillCartException(
                message=f"Job with ID '{job_id}' not found.", status_code=404
            )
        raise SkillCartException(
            message=f"Failed to fetch job details for job ID '{job_id}'.",
            status_code=502,
            errors=str(exc),
        )
    except requests.RequestException as exc:
        raise SkillCartException(
            message="Failed to connect to the jobs service.",
            status_code=502,
            errors=str(exc),
        )

    job_description = _build_job_description(job)
    result = await ResumeEvaluationService.evaluate_resume(resume, job_description)
    return success_response(data=result, message="Resume evaluated successfully")


@router.post("/career/match", response_model=ApiResponse)
async def match_career_endpoint(req: MatchRequest):

    resume = resolve_resume(req.res_id)

    result = await CareerMatchingService.match_career(resume=resume, top_k=req.top_k)

    return success_response(
        data=result, message="Recommended jobs fetched successfully"
    )


@router.post("/career/enhance", response_model=ApiResponse)
async def enhance_career_endpoint(req: EnhanceRequest):
    """Generate Resume Flex bullets, cover letter, and a milestone learning roadmap."""
    resume = resolve_resume(req.res_id)
    result = await CareerEnhancementService.enhance_career(resume, req.match_report)
    return success_response(
        data=result, message="Career enhancement package generated successfully"
    )


@router.post("/interview/prepare", response_model=ApiResponse)
async def prepare_interview_endpoint(req: PrepareInterviewRequest):
    """Generate tailored interview prep questions based on category, resume, and job details."""
    resume = resolve_resume(req.res_id)
    
    # 1. Parse and validate job_id
    try:
        job_id = int(req.job_id.strip())
    except ValueError:
        raise SkillCartException(
            message="'job_id' must be a valid integer.",
            status_code=400
        )

    # 2. Fetch job details from Railway API
    try:
        job = await anyio.to_thread.run_sync(railway_client.get_job, job_id)
    except requests.HTTPError as exc:
        if exc.response is not None and exc.response.status_code == 404:
            raise SkillCartException(
                message=f"Job with ID '{job_id}' not found.",
                status_code=404
            )
        raise SkillCartException(
            message=f"Failed to fetch job details for job ID '{job_id}'.",
            status_code=502,
            errors=str(exc)
        )
    except requests.RequestException as exc:
        raise SkillCartException(
            message="Failed to connect to the jobs service.",
            status_code=502,
            errors=str(exc)
        )

    # 3. Build job description string
    job_description = _build_job_description(job)
    
    # 4. Normalize and map the category option
    category = req.category.strip().title()
    if category == "Hr":
        category = "HR"
    elif category == "Company":
        category = "Company-Specific"

    result = await InterviewIntelligenceService.prepare_interview(
        resume=resume, 
        job_description=job_description,
        category=category
    )
    return success_response(data=result, message="Interview preparation questions generated successfully")



@router.post("/copilot/guidance", response_model=ApiResponse)
async def guidance_endpoint(req: GuidanceRequest):
    """Ingest evaluation and match data to build a strategic Career Guidance Report."""
    resume = resolve_resume(req.res_id)
    result = await CareerCopilotService.generate_guidance(
        resume, req.evaluation, req.match
    )
    return success_response(
        data=result, message="Career guidance report generated successfully"
    )


@router.post("/copilot/chat", response_model=ApiResponse)
async def chat_endpoint(req: ChatRequest):
    """Chat interactively with the Career Copilot using query and optional resume context."""
    resume_data = None
    if req.res_id:
        try:
            resume_data = get_resume_ai_response_data(req.res_id)
            if not resume_data:
                resume_data = get_resume_data(req.res_id)
        except Exception:
            # Gracefully ignore any DB lookup errors and proceed without resume context
            resume_data = None
            
    result = await CareerCopilotService.chat(
        query=req.query,
        resume_data=resume_data
    )
    return success_response(
        data=result, message="Copilot response generated successfully"
    )
