from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
import pytest
import requests
from app.main import app
from app.ai.services.models import (
    ResumeSchema, 
    GenResumeSchema,
    ContactDetails, 
    SkillCategory,
    ResumeEvaluationSchema, 
    ATSAnalysis,
    GrammarFormattingReport,
    JobDescriptionAlignment,
    CareerMatchSchema,
    MatchScoreBreakdown,
    ResumeAnalysisReportSchema,
    ScoresBreakdown,
    GrammarAnalysis,
    StructureAnalysis,
    FormattingAnalysis,
    ContentAnalysis,
    ATSAnalysisReport,
    SuggestionsCategorized,
    CareerEnhancementSchema,
    InterviewPrepSchema,
    CareerGuidanceReportSchema,
    ChatResponseSchema,
    ChatMessage
)

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_parse_resume_endpoint():
    mock_resume = ResumeSchema(
        name="Alice Smith",
        contact=ContactDetails(
            email="alice@smith.com", 
            phone="987654", 
            location="SF"
        ),
        education=[],
        experience=[],
        projects=[],
        skills=[
            SkillCategory(category="Programming", skills=["Python"])
        ],
        certifications=[]
    )
    raw_text = "Alice Smith\nEmail: alice@smith.com\nEducation\nSkills\nPython"
    with patch("app.api.v1.endpoints.extract_text_from_file", return_value=raw_text):
        with patch("app.api.v1.endpoints.ResumeIntelligenceService.parse_resume", return_value=mock_resume) as mock_parse, \
             patch("app.api.v1.endpoints.save_resume_data") as mock_save:
            file_data = {"file": ("resume.pdf", b"fake pdf bytes", "application/pdf")}
            response = client.post("/api/v1/resume/parse", files=file_data)
            assert response.status_code == 200
            json_data = response.json()
            assert json_data["success"] is True
            assert json_data["data"]["name"] == "Alice Smith"
            assert "res_id" not in json_data["data"]
            mock_parse.assert_called_once_with(raw_text)
            mock_save.assert_not_called()

def test_parse_resume_endpoint_non_resume_file():
    with patch("app.api.v1.endpoints.extract_text_from_file", return_value="Invoice total amount due 2500 INR"), \
         patch("app.api.v1.endpoints.ResumeIntelligenceService.parse_resume") as mock_parse:
        file_data = {"file": ("invoice.pdf", b"fake pdf bytes", "application/pdf")}
        response = client.post("/api/v1/resume/parse", files=file_data)

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"] is None
    assert json_data["message"] == "Uploaded file does not appear to be a resume."
    mock_parse.assert_not_called()

def test_generate_resume_endpoint():
    payload = {
        "name": "John Doe",
        "contact": {
            "email": "john@example.com",
            "phone": "1234567890",
            "location": "New York, NY",
            "linkedin": "https://linkedin.com/in/johndoe"
        },
        "education": [
            {
                "institution": "ABC University",
                "degree": "Bachelor of Engineering",
                "major": "Computer Science",
                "start_date": "2020",
                "end_date": "2024",
                "gpa": "8.7/10"
            }
        ],
        "experience": [
            {
                "company": "SkillCart",
                "role": "Backend Intern",
                "start_date": "Jan 2026",
                "end_date": "Jul 2026",
                "highlights": [
                    "Built FastAPI endpoints",
                    "Improved resume processing workflows"
                ]
            }
        ],
        "projects": [
            {
                "name": "Resume Optimizer",
                "description": "A project to score resumes for ATS compatibility.",
                "highlights": [
                    "Created matching logic",
                    "Integrated document parsing"
                ],
                "url": "https://github.com/johndoe/resume-optimizer"
            }
        ],
        "skills": [
            {
                "category": "Backend",
                "skills": ["Python", "FastAPI", "SQL"]
            }
        ],
        "certifications": [
            {
                "name": "AWS Cloud Practitioner",
                "issuer": "Amazon",
                "issue_date": "2025",
                "url": "https://example.com/aws-cert"
            }
        ]
    }

    polished_resume = GenResumeSchema(
        name="John Doe",
        contact=ContactDetails(
            email="john@example.com",
            phone="1234567890",
            location="New York, NY",
            linkedin="https://linkedin.com/in/johndoe"
        ),
        education=[],
        experience=[],
        projects=[],
        skills=[],
        certifications=[]
    )

    with patch("app.api.v1.endpoints.ResumeGenerationService.improve_gen_resume", return_value=polished_resume) as mock_improve, \
         patch("app.api.v1.endpoints.save_resume_data") as mock_save:
        response = client.post("/api/v1/resume/generate", json=payload)

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["parsed_data"]["name"] == "John Doe"
    assert json_data["data"]["parsed_data"]["contact"]["email"] == "john@example.com"
    generated_res_id = json_data["data"]["res_id"]
    assert json_data["data"]["resume"]["res_id"] == generated_res_id
    assert json_data["data"]["download_url"].endswith(f"/api/v1/resume/{generated_res_id}/download")

    mock_improve.assert_called_once()
    draft_resume = mock_improve.call_args.args[0]
    assert draft_resume.name == "John Doe"
    assert draft_resume.skills[0].skills == ["Python", "FastAPI", "SQL"]
    mock_save.assert_called_once()
    assert mock_save.call_args.kwargs["res_id"] == generated_res_id
    assert mock_save.call_args.kwargs["name"] == "John Doe"
    assert mock_save.call_args.kwargs["parsed_data"]["name"] == "John Doe"

def test_generate_resume_endpoint_missing_parameters():
    response = client.post("/api/v1/resume/generate", json={})
    assert response.status_code == 422
    json_data = response.json()
    assert json_data["success"] is False
    assert "validation failed" in json_data["message"].lower()

def test_download_resume_endpoint():
    generated_resume = GenResumeSchema(
        name="John Doe",
        contact=ContactDetails(email="john@example.com", phone="12345678", location="New York, NY"),
        education=[],
        experience=[],
        projects=[],
        skills=[],
        certifications=[]
    )
    with patch("app.api.v1.endpoints.get_resume_data", return_value=generated_resume.model_dump(mode="json")):
        response = client.get(f"/api/v1/resume/{generated_resume.res_id}/download")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith(
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    assert "attachment;" in response.headers["content-disposition"]
    assert response.headers["content-disposition"].endswith("-resume.docx\"")
    assert response.content.startswith(b"PK")

def test_download_resume_endpoint_not_found():
    with patch("app.api.v1.endpoints.get_resume_data", return_value=None):
        response = client.get("/api/v1/resume/missing-id/download")

    assert response.status_code == 404
    json_data = response.json()
    assert json_data["success"] is False
    assert "not found in the database" in json_data["message"]

def test_evaluate_resume_by_res_id_endpoint(dummy_resume, dummy_evaluation):
    with patch("app.api.v1.endpoints.get_resume_data", return_value=dummy_resume.model_dump(mode="json")) as mock_get_db, \
         patch("app.api.v1.endpoints.railway_client.get_job", return_value={
             "id": 1,
             "job_title": "Software Engineer",
             "department": "Engineering",
             "employment_type": "Full-Time",
             "work_mode": "On-site",
             "location": "Coimbatore, Tamil Nadu, India",
             "experience_min": 0,
             "experience_max": 1,
             "project_role": "Software Engineer I",
             "project_role_description": "Build and scale product features.",
             "summary": "Join our engineering team to build customer-facing products.",
             "education": "Bachelor's degree in Computer Science",
             "additional_information": "Technical assessment followed by interviews.",
             "company": {
                 "company_name": "BluepeakVentures Limited",
                 "description": "Telecommunications company serving clients across India."
             },
             "responsibilities": [
                 "Design scalable software applications",
                 "Write unit and integration tests"
             ],
             "required_skills": ["RESTful API Design", "SQL"],
             "preferred_skills": ["AWS"],
             "professional_skills": ["Problem-solving"]
         }) as mock_get_job, \
         patch("app.api.v1.endpoints.ResumeEvaluationService.evaluate_resume", return_value=dummy_evaluation) as mock_eval:
        
        payload = {
            "res_id": "dummy-uuid-1234",
            "job_id": "1"
        }
        response = client.post("/api/v1/resume/evaluate", json=payload)
        assert response.status_code == 200
        json_data = response.json()
        assert json_data["success"] is True
        assert json_data["data"]["ats_analysis"]["score"] == 85
        mock_get_db.assert_called_once_with("dummy-uuid-1234")
        mock_get_job.assert_called_once_with(1)
        mock_eval.assert_called_once()

        _, job_description = mock_eval.call_args.args
        assert "Job Title: Software Engineer" in job_description
        assert "Company: BluepeakVentures Limited" in job_description
        assert "Responsibilities: Design scalable software applications, Write unit and integration tests" in job_description
        assert "salary_min" not in job_description

def test_evaluate_resume_endpoint_missing_parameters():
    payload = {
        "res_id": "dummy-uuid-1234"
    }
    response = client.post("/api/v1/resume/evaluate", json=payload)
    assert response.status_code == 422
    json_data = response.json()
    assert json_data["success"] is False
    assert "validation failed" in json_data["message"].lower()

def test_evaluate_resume_endpoint_not_found_in_db():
    with patch("app.api.v1.endpoints.get_resume_data", return_value=None) as mock_get_db:
        payload = {
            "res_id": "nonexistent-uuid",
            "job_id": "1"
        }
        response = client.post("/api/v1/resume/evaluate", json=payload)
        assert response.status_code == 404
        json_data = response.json()
        assert json_data["success"] is False
        assert "not found in the database" in json_data["message"]

def test_evaluate_resume_endpoint_job_not_found(dummy_resume):
    mock_response = MagicMock()
    mock_response.status_code = 404
    http_error = requests.HTTPError(response=mock_response)

    with patch("app.api.v1.endpoints.get_resume_data", return_value=dummy_resume.model_dump(mode="json")), \
         patch("app.api.v1.endpoints.railway_client.get_job", side_effect=http_error):
        response = client.post(
            "/api/v1/resume/evaluate",
            json={"res_id": "dummy-uuid-1234", "job_id": "999"}
        )

    assert response.status_code == 404
    json_data = response.json()
    assert json_data["success"] is False
    assert "Job with ID '999' not found." in json_data["message"]

# Fixtures for API endpoints testing

@pytest.fixture
def dummy_resume():
    return ResumeSchema(
        name="John Doe",
        contact=ContactDetails(
            email="john@example.com", 
            phone="12345678", 
            location="New York, NY"
        ),
        education=[],
        experience=[],
        projects=[],
        skills=[],
        certifications=[]
    )

@pytest.fixture
def dummy_evaluation():
    return ResumeEvaluationSchema(
        ats_analysis=ATSAnalysis(
            score=85,
            findings=["Clean layouts used"],
            missing_keywords=["FastAPI"],
            missing_sections=[]
        ),
        grammar_formatting=GrammarFormattingReport(
            grammar_issues=[],
            formatting_issues=[]
        ),
        jd_alignment=JobDescriptionAlignment(
            relevance_score=80,
            alignment_summary="Strong match.",
            gaps=[]
        ),
        suggestions=[]
    )


@pytest.fixture
def dummy_analysis():
    return ResumeAnalysisReportSchema(
        overall_score=75,
        summary="Good resume.",
        scores=ScoresBreakdown(
            grammar=80,
            structure=85,
            formatting=70,
            content=75,
            ats=80
        ),
        grammar_analysis=GrammarAnalysis(
            total_errors=0,
            errors=[]
        ),
        structure_analysis=StructureAnalysis(
            missing_sections=["Professional Summary"],
            duplicate_sections=[],
            empty_sections=[],
            incorrect_order=[],
            recommendations=[]
        ),
        formatting_analysis=FormattingAnalysis(
            issues=[],
            recommendations=[]
        ),
        content_analysis=ContentAnalysis(
            weak_statements=[],
            improved_versions=[],
            missing_information=[]
        ),
        ats_analysis=ATSAnalysisReport(
            ats_friendly=True,
            issues=[]
        ),
        strengths=["Strong programming skills"],
        weaknesses=["Missing professional summary"],
        suggestions=SuggestionsCategorized(
            high_priority=[],
            medium_priority=[],
            low_priority=[]
        )
    )


def test_analyze_resume_endpoint(dummy_resume, dummy_analysis):
    with patch("app.api.v1.endpoints.extract_text_from_file", return_value="fake resume content"), \
         patch("app.api.v1.endpoints.ResumeIntelligenceService.parse_resume", return_value=dummy_resume) as mock_parse, \
         patch("app.api.v1.endpoints.save_resume_data") as mock_save, \
         patch("app.api.v1.endpoints.ResumeAnalysisService.analyze_resume", return_value=dummy_analysis) as mock_analyze:
        
        file_data = {"file": ("resume.pdf", b"fake pdf bytes", "application/pdf")}
        response = client.post("/api/v1/resume/analyze", files=file_data)
        
        assert response.status_code == 200
        json_data = response.json()
        assert json_data["success"] is True
        assert json_data["data"]["overall_score"] == 75
        assert json_data["data"]["summary"] == "Good resume."
        mock_parse.assert_called_once_with("fake resume content")
        mock_save.assert_called_once()
        mock_analyze.assert_called_once_with(dummy_resume)


def test_match_career_endpoint(dummy_resume):
    mock_result = {
        "resume_id": "dummy-uuid-1234",
        "recommended_jobs": [{"id": 101, "title": "Python Developer"}],
        "total": 1
    }
    with patch("app.api.v1.endpoints.get_resume_data", return_value=dummy_resume.model_dump(mode="json")), \
         patch("app.api.v1.endpoints.CareerMatchingService.match_career", return_value=mock_result) as mock_match:
         
        payload = {
            "res_id": "dummy-uuid-1234",
            "top_k": 5
        }
        response = client.post("/api/v1/career/match", json=payload)
        assert response.status_code == 200
        json_data = response.json()
        assert json_data["success"] is True
        assert json_data["data"]["total"] == 1
        assert json_data["data"]["recommended_jobs"][0]["title"] == "Python Developer"
        mock_match.assert_called_once()


def test_enhance_career_endpoint(dummy_resume):
    mock_enhance = CareerEnhancementSchema(
        resume_flex=[],
        role_specific_rewrite_recommendations=["Add certifications section"],
        learning_roadmap=[],
        cover_letter="Dear Hiring Manager..."
    )
    dummy_match_report = CareerMatchSchema(
        overall_match_score=90,
        score_breakdown=MatchScoreBreakdown(
            skills_score=90,
            experience_score=85,
            education_score=95
        ),
        matching_skills=["Python"],
        missing_skills=[],
        experience_match_details="Good",
        education_match_details="Good",
        skill_gaps=[],
        summary="Matches target role"
    )
    with patch("app.api.v1.endpoints.get_resume_data", return_value=dummy_resume.model_dump(mode="json")), \
         patch("app.api.v1.endpoints.CareerEnhancementService.enhance_career", return_value=mock_enhance) as mock_enhance_service:
         
        payload = {
            "res_id": "dummy-uuid-1234",
            "match_report": dummy_match_report.model_dump(mode="json")
        }
        response = client.post("/api/v1/career/enhance", json=payload)
        assert response.status_code == 200
        json_data = response.json()
        assert json_data["success"] is True
        assert json_data["data"]["cover_letter"] == "Dear Hiring Manager..."
        mock_enhance_service.assert_called_once()


def test_enhance_career_endpoint_fetches_ai_response_json(dummy_resume):
    mock_enhance = CareerEnhancementSchema(
        resume_flex=[],
        role_specific_rewrite_recommendations=["Add certifications section"],
        learning_roadmap=[],
        cover_letter="Dear Hiring Manager..."
    )
    dummy_match_report = CareerMatchSchema(
        overall_match_score=90,
        score_breakdown=MatchScoreBreakdown(
            skills_score=90,
            experience_score=85,
            education_score=95
        ),
        matching_skills=["Python"],
        missing_skills=[],
        experience_match_details="Good",
        education_match_details="Good",
        skill_gaps=[],
        summary="Matches target role"
    )

    with patch("app.api.v1.endpoints.get_resume_ai_response_data", return_value=dummy_resume.model_dump(mode="json")) as mock_ai_data, \
         patch("app.api.v1.endpoints.get_resume_data") as mock_legacy_data, \
         patch("app.api.v1.endpoints.CareerEnhancementService.enhance_career", return_value=mock_enhance) as mock_enhance_service:
        response = client.post(
            "/api/v1/career/enhance",
            json={
                "res_id": "123",
                "match_report": dummy_match_report.model_dump(mode="json")
            }
        )

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["cover_letter"] == "Dear Hiring Manager..."
    mock_ai_data.assert_called_once_with("123")
    mock_legacy_data.assert_not_called()
    resume_arg, _ = mock_enhance_service.call_args.args
    assert resume_arg.name == dummy_resume.name


def test_prepare_interview_endpoint(dummy_resume):
    mock_prep = InterviewPrepSchema(questions=[])
    with patch("app.api.v1.endpoints.get_resume_data", return_value=dummy_resume.model_dump(mode="json")), \
         patch("app.api.v1.endpoints.railway_client.get_job", return_value={
             "id": 1,
             "job_title": "Software Engineer",
             "company": {"company_name": "BluepeakVentures Limited", "description": "Telecommunications"}
         }), \
         patch("app.api.v1.endpoints.InterviewIntelligenceService.prepare_interview", return_value=mock_prep) as mock_prep_service:
         
        payload = {
            "res_id": "dummy-uuid-1234",
            "job_id": "1",
            "category": "Technical"
        }
        response = client.post("/api/v1/interview/prepare", json=payload)
        assert response.status_code == 200
        json_data = response.json()
        assert json_data["success"] is True
        assert "questions" in json_data["data"]
        mock_prep_service.assert_called_once()


def test_prepare_interview_endpoint_optional_res_id():
    mock_prep = InterviewPrepSchema(questions=[])
    with patch("app.api.v1.endpoints.railway_client.get_job", return_value={
             "id": 1,
             "job_title": "Software Engineer",
             "company": {"company_name": "BluepeakVentures Limited", "description": "Telecommunications"}
         }), \
         patch("app.api.v1.endpoints.InterviewIntelligenceService.prepare_interview", return_value=mock_prep) as mock_prep_service:
         
        payload = {
            "job_id": "1",
            "category": "Technical"
        }
        response = client.post("/api/v1/interview/prepare", json=payload)
        assert response.status_code == 200
        json_data = response.json()
        assert json_data["success"] is True
        assert "questions" in json_data["data"]
        mock_prep_service.assert_called_once()


def test_prepare_interview_endpoint_wrong_res_id():
    mock_prep = InterviewPrepSchema(questions=[])
    with patch("app.api.v1.endpoints.get_resume_ai_response_data", side_effect=Exception("Database error")), \
         patch("app.api.v1.endpoints.railway_client.get_job", return_value={
             "id": 1,
             "job_title": "Software Engineer",
             "company": {"company_name": "BluepeakVentures Limited", "description": "Telecommunications"}
         }), \
         patch("app.api.v1.endpoints.InterviewIntelligenceService.prepare_interview", return_value=mock_prep) as mock_prep_service:
         
        payload = {
            "res_id": "wrong-id",
            "job_id": "1",
            "category": "Technical"
        }
        response = client.post("/api/v1/interview/prepare", json=payload)
        assert response.status_code == 200
        json_data = response.json()
        assert json_data["success"] is True
        assert "questions" in json_data["data"]
        mock_prep_service.assert_called_once()
        _, kwargs = mock_prep_service.call_args
        assert kwargs.get("resume") is None


def test_guidance_endpoint(dummy_resume, dummy_evaluation):
    mock_guidance = CareerGuidanceReportSchema(
        career_advice="Keep learning cloud systems.",
        resume_improvements_summary=[],
        salary_insights="$100k-$120k",
        hiring_chances=80,
        next_steps=[],
        study_suggestions=[]
    )
    dummy_match_report = CareerMatchSchema(
        overall_match_score=90,
        score_breakdown=MatchScoreBreakdown(
            skills_score=90,
            experience_score=85,
            education_score=95
        ),
        matching_skills=["Python"],
        missing_skills=[],
        experience_match_details="Good",
        education_match_details="Good",
        skill_gaps=[],
        summary="Matches target role"
    )
    with patch("app.api.v1.endpoints.get_resume_data", return_value=dummy_resume.model_dump(mode="json")), \
         patch("app.api.v1.endpoints.CareerCopilotService.generate_guidance", return_value=mock_guidance) as mock_guidance_service:
         
        payload = {
            "res_id": "dummy-uuid-1234",
            "evaluation": dummy_evaluation.model_dump(mode="json"),
            "match": dummy_match_report.model_dump(mode="json")
        }
        response = client.post("/api/v1/copilot/guidance", json=payload)
        assert response.status_code == 200
        json_data = response.json()
        assert json_data["success"] is True
        assert json_data["data"]["salary_insights"] == "$100k-$120k"
        mock_guidance_service.assert_called_once()


def test_chat_endpoint(dummy_resume):
    mock_chat_response = ChatResponseSchema(
        response="Here is my response.",
        suggested_followups=["How to learn Docker?"]
    )
    dummy_match_report = CareerMatchSchema(
        overall_match_score=90,
        score_breakdown=MatchScoreBreakdown(
            skills_score=90,
            experience_score=85,
            education_score=95
        ),
        matching_skills=["Python"],
        missing_skills=[],
        experience_match_details="Good",
        education_match_details="Good",
        skill_gaps=[],
        summary="Matches target role"
    )
    with patch("app.api.v1.endpoints.get_resume_data", return_value=dummy_resume.model_dump(mode="json")), \
         patch("app.api.v1.endpoints.CareerCopilotService.chat", return_value=mock_chat_response) as mock_chat_service:
         
        payload = {
            "res_id": "dummy-uuid-1234",
            "message": "Hi",
            "history": [{"role": "user", "content": "Hello"}],
            "career_match": dummy_match_report.model_dump(mode="json")
        }
        response = client.post("/api/v1/copilot/chat", json=payload)
        assert response.status_code == 200
        json_data = response.json()
        assert json_data["success"] is True
        assert json_data["data"]["response"] == "Here is my response."
        mock_chat_service.assert_called_once()
