import pytest
from unittest.mock import MagicMock, patch
from app.ai.services.models import (
    ResumeSchema, 
    ContactDetails,
    ResumeEvaluationSchema, 
    ATSAnalysis,
    GrammarFormattingReport,
    JobDescriptionAlignment,
    CareerMatchSchema,
    MatchScoreBreakdown,
    CareerEnhancementSchema, 
    InterviewPrepSchema, 
    CareerGuidanceReportSchema, 
    ChatResponseSchema,
    ChatMessage
)
from app.ai.services.resume_intel import ResumeIntelligenceService
from app.ai.services.resume_generate import ResumeGenerationService
from app.ai.services.resume_eval import ResumeEvaluationService
from app.ai.services.career_match import CareerMatchingService
from app.ai.services.career_enhance import CareerEnhancementService
from app.ai.services.interview import InterviewIntelligenceService
from app.ai.services.copilot import CareerCopilotService

# Create mock data fixtures

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
            findings=["Standard font and clean layouts used"],
            missing_keywords=["FastAPI", "Docker"],
            missing_sections=["Certifications"]
        ),
        grammar_formatting=GrammarFormattingReport(
            grammar_issues=[],
            formatting_issues=[]
        ),
        jd_alignment=JobDescriptionAlignment(
            relevance_score=80,
            alignment_summary="Strong match for Python developer roles.",
            gaps=["Needs Cloud experience"]
        ),
        suggestions=[]
    )

@pytest.fixture
def dummy_match():
    return CareerMatchSchema(
        overall_match_score=90,
        score_breakdown=MatchScoreBreakdown(
            skills_score=90,
            experience_score=85,
            education_score=95
        ),
        matching_skills=["Python", "FastAPI"],
        missing_skills=["Kubernetes"],
        experience_match_details="Meets minimum requirement.",
        education_match_details="Aligns fully.",
        skill_gaps=[],
        summary="Matches target role closely."
    )


@pytest.mark.asyncio
async def test_resume_intelligence_service(dummy_resume):
    mock_provider = MagicMock()
    mock_provider.generate_structured_output.return_value = dummy_resume
    
    with patch("app.ai.providers.factory.LLMProviderFactory.get_provider", return_value=mock_provider):
        result = await ResumeIntelligenceService.parse_resume("raw resume text")
        assert result.name == "John Doe"
        assert result.contact.email == "john@example.com"
        mock_provider.generate_structured_output.assert_called_once()


@pytest.mark.asyncio
async def test_resume_generation_service(dummy_resume):
    mock_provider = MagicMock()
    mock_provider.generate_structured_output.return_value = dummy_resume

    with patch("app.ai.services.resume_generate.GeminiProvider", return_value=mock_provider):
        result = await ResumeGenerationService.improve_resume(dummy_resume)
        assert result.name == "John Doe"
        assert result.contact.email == "john@example.com"
        mock_provider.generate_structured_output.assert_called_once()


@pytest.mark.asyncio
async def test_resume_evaluation_service(dummy_resume, dummy_evaluation):
    mock_provider = MagicMock()
    mock_provider.generate_structured_output.return_value = dummy_evaluation
    
    with patch("app.ai.providers.factory.LLMProviderFactory.get_provider", return_value=mock_provider):
        result = await ResumeEvaluationService.evaluate_resume(dummy_resume, "JD text")
        assert result.ats_analysis.score == 85
        assert "FastAPI" in result.ats_analysis.missing_keywords


@pytest.mark.asyncio
async def test_career_matching_service(dummy_resume):
    mock_jobs = [{"job_id": 101, "score": 0.95}]
    mock_job_detail = {"id": 101, "title": "Python Developer", "company": "Tech Inc"}
    
    with patch("app.ai.services.career_match.build_resume_document", return_value="dummy doc"), \
         patch("app.ai.services.career_match.search_jobs", return_value=mock_jobs) as mock_search, \
         patch("app.ai.services.career_match.railway_client.get_job", return_value=mock_job_detail) as mock_get_job:
         
        result = await CareerMatchingService.match_career(dummy_resume, top_k=5)
        
        assert result["resume_id"] == dummy_resume.res_id
        assert len(result["recommended_jobs"]) == 1
        assert result["recommended_jobs"][0]["title"] == "Python Developer"
        assert result["total"] == 1
        
        mock_search.assert_called_once_with(document="dummy doc", top_k=5)
        mock_get_job.assert_called_once_with(101)


@pytest.mark.asyncio
async def test_career_enhancement_service(dummy_resume, dummy_match):
    mock_enhance = CareerEnhancementSchema(
        resume_flex=[],
        role_specific_rewrite_recommendations=["Add certifications section"],
        learning_roadmap=[],
        cover_letter="Dear Hiring Manager..."
    )
    mock_provider = MagicMock()
    mock_provider.generate_structured_output.return_value = mock_enhance
    
    with patch("app.ai.providers.factory.LLMProviderFactory.get_provider", return_value=mock_provider):
        result = await CareerEnhancementService.enhance_career(dummy_resume, dummy_match)
        assert result.cover_letter.startswith("Dear")
        assert "Add certifications section" in result.role_specific_rewrite_recommendations


@pytest.mark.asyncio
async def test_interview_prep_service(dummy_resume):
    mock_prep = InterviewPrepSchema(questions=[])
    mock_provider = MagicMock()
    mock_provider.generate_structured_output.return_value = mock_prep
    
    with patch("app.ai.providers.factory.LLMProviderFactory.get_provider", return_value=mock_provider):
        result = await InterviewIntelligenceService.prepare_interview(dummy_resume, "JD text")
        assert isinstance(result, InterviewPrepSchema)


@pytest.mark.asyncio
async def test_copilot_service_guidance(dummy_resume, dummy_evaluation, dummy_match):
    mock_guidance = CareerGuidanceReportSchema(
        career_advice="Keep learning cloud systems.",
        resume_improvements_summary=[],
        salary_insights="$100k-$120k",
        hiring_chances=80,
        next_steps=[],
        study_suggestions=[]
    )
    mock_provider = MagicMock()
    mock_provider.generate_structured_output.return_value = mock_guidance
    
    with patch("app.ai.providers.factory.LLMProviderFactory.get_provider", return_value=mock_provider):
        result = await CareerCopilotService.generate_guidance(dummy_resume, dummy_evaluation, dummy_match)
        assert result.hiring_chances == 80
        assert result.salary_insights == "$100k-$120k"


@pytest.mark.asyncio
async def test_copilot_service_chat(dummy_resume, dummy_match):
    mock_chat_response = ChatResponseSchema(
        response="Here is my response.",
        suggested_followups=["How to learn Docker?"]
    )
    mock_provider = MagicMock()
    mock_provider.generate_structured_output.return_value = mock_chat_response
    
    with patch("app.ai.providers.factory.LLMProviderFactory.get_provider", return_value=mock_provider):
        result = await CareerCopilotService.chat(
            message="Hi",
            history=[ChatMessage(role="user", content="Hello")],
            resume=dummy_resume,
            career_match=dummy_match
        )
        assert result.response == "Here is my response."
        assert "How to learn Docker?" in result.suggested_followups
