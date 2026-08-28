from typing import List, Optional
from pydantic import BaseModel, Field
from uuid import UUID, uuid4

# =====================================================================
# Engine 1: Resume Intelligence Engine Models
# =====================================================================

class ContactDetails(BaseModel):
    email: Optional[str] = Field(None, description="Contact email address")
    phone: Optional[str] = Field(None, description="Contact phone number with area code")
    location: Optional[str] = Field(None, description="Candidate's location (e.g. City, State or City, Country)")
    linkedin: Optional[str] = Field(None, description="LinkedIn profile link")
    github: Optional[str] = Field(None, description="GitHub profile link")
    portfolio: Optional[str] = Field(None, description="Personal portfolio or website link")

class EducationItem(BaseModel):
    institution: str = Field(..., description="Name of the university, college, or school")
    degree: Optional[str] = Field(None, description="Degree or program title (e.g. BS, MS, PhD, High School Diploma)")
    major: Optional[str] = Field(None, description="Field of study or major")
    start_date: Optional[str] = Field(None, description="Start date (month/year, year, or equivalent)")
    end_date: Optional[str] = Field(None, description="End date (month/year, year, or 'Present')")
    gpa: Optional[str] = Field(None, description="GPA or academic grade out of scale")

class ExperienceItem(BaseModel):
    company: str = Field(..., description="Organization or company name")
    role: str = Field(..., description="Job role or title held")
    start_date: Optional[str] = Field(None, description="Start date")
    end_date: Optional[str] = Field(None, description="End date or 'Present'")
    highlights: List[str] = Field(default_factory=list, description="Key duties and quantifiable accomplishments")

class ProjectItem(BaseModel):
    name: str = Field(..., description="Name of the project")
    description: str = Field(..., description="Overview of project goal, architecture, or technologies used")
    highlights: List[str] = Field(default_factory=list, description="Detailed achievements or tasks performed")
    url: Optional[str] = Field(None, description="Link to source code repository or deployment URL")

class SkillCategory(BaseModel):
    category: str = Field(..., description="Skill category name (e.g. Programming Languages, Frameworks, Databases, Tools, Soft Skills)")
    skills: List[str] = Field(..., description="Normalized names of skills in this category")

class CertificationItem(BaseModel):
    name: str = Field(..., description="Name of the certification")
    issuer: Optional[str] = Field(None, description="Issuing organization")
    issue_date: Optional[str] = Field(None, description="Date of completion or issuance")
    url: Optional[str] = Field(None, description="Credential ID or credential link")

class ResumeSchema(BaseModel):
    name: str = Field(..., description="Candidate's full name")
    contact: ContactDetails = Field(..., description="Candidate contact methods and social links")
    education: List[EducationItem] = Field(default_factory=list, description="Academic records list")
    experience: List[ExperienceItem] = Field(default_factory=list, description="Professional experience timeline list")
    projects: List[ProjectItem] = Field(default_factory=list, description="Key projects list")
    skills: List[SkillCategory] = Field(default_factory=list, description="Categorized list of skills")
    certifications: List[CertificationItem] = Field(default_factory=list, description="Professional certifications list")
    
class GenResumeSchema(BaseModel):
    res_id : UUID = Field(default_factory=uuid4)
    name: str = Field(..., description="Candidate's full name")
    contact: ContactDetails = Field(..., description="Candidate contact methods and social links")
    education: List[EducationItem] = Field(default_factory=list, description="Academic records list")
    experience: List[ExperienceItem] = Field(default_factory=list, description="Professional experience timeline list")
    projects: List[ProjectItem] = Field(default_factory=list, description="Key projects list")
    skills: List[SkillCategory] = Field(default_factory=list, description="Categorized list of skills")
    certifications: List[CertificationItem] = Field(default_factory=list, description="Professional certifications list")


# =====================================================================
# Engine 2: Resume Evaluation Engine Models
# =====================================================================

class ATSAnalysis(BaseModel):
    score: int = Field(..., ge=0, le=100, description="Overall ATS suitability score out of 100")
    findings: List[str] = Field(..., description="Observations regarding text density, layout friendliness, tables, fonts, or header styling")
    missing_keywords: List[str] = Field(..., description="Keywords required or standard for the role that are absent from the resume")
    missing_sections: List[str] = Field(..., description="Standard sections missing from the resume")

class GrammarFormattingReport(BaseModel):
    grammar_issues: List[str] = Field(..., description="Spelling, syntax, tense inconsistencies, or punctuation mistakes")
    formatting_issues: List[str] = Field(..., description="Inconsistent margins, dates alignment, list bullet shapes, or font styles")

class JobDescriptionAlignment(BaseModel):
    relevance_score: int = Field(..., ge=0, le=100, description="Match score of resume contents with the given job description (0-100)")
    alignment_summary: str = Field(..., description="A summary explaining the strengths of alignment and critical mismatch points")
    gaps: List[str] = Field(..., description="Major gaps between the candidate's background and the JD requirements")

class ActionableSuggestion(BaseModel):
    section: str = Field(..., description="Target section (e.g. Summary, Experience, Projects)")
    current_text: Optional[str] = Field(None, description="Current text or context to be improved")
    suggested_change: str = Field(..., description="Recommended rewrite or addition")
    rationale: str = Field(..., description="Why this suggestion improves ATS or hiring impact")

class ResumeEvaluationSchema(BaseModel):
    ats_analysis: ATSAnalysis = Field(..., description="ATS parser friendliness and keyword checks")
    grammar_formatting: GrammarFormattingReport = Field(..., description="Grammar and page design feedback")
    jd_alignment: JobDescriptionAlignment = Field(..., description="Evaluation of alignment with the target JD (defaults to basic scores if JD is not provided)")
    suggestions: List[ActionableSuggestion] = Field(..., description="Actionable updates with step-by-step rewrites")


# =====================================================================
# Engine 3: Career Matching Engine Models
# =====================================================================

class MatchScoreBreakdown(BaseModel):
    skills_score: int = Field(..., ge=0, le=100, description="Technical and soft skills alignment score (0-100)")
    experience_score: int = Field(..., ge=0, le=100, description="Work history and seniority level score (0-100)")
    education_score: int = Field(..., ge=0, le=100, description="Academic degree requirements score (0-100)")

class SkillGapItem(BaseModel):
    skill: str = Field(..., description="Name of the missing or insufficient skill")
    importance: str = Field(..., description="Criticality level for the target role: 'High', 'Medium', or 'Low'")
    learning_priority: int = Field(..., description="Priority sequence number (1 being highest/immediate)")
    estimated_hours: int = Field(..., description="Estimated hours of learning to reach a baseline capability")

class CareerMatchSchema(BaseModel):
    overall_match_score: int = Field(..., ge=0, le=100, description="Overall matching score (0-100) combining skills, experience, and education")
    score_breakdown: MatchScoreBreakdown = Field(..., description="Score breakdown across primary categories")
    matching_skills: List[str] = Field(..., description="Skills listed in the resume that match the job description")
    missing_skills: List[str] = Field(..., description="Skills specified in the JD that are not found in the resume")
    experience_match_details: str = Field(..., description="Detailed description of experience alignment or shortcomings")
    education_match_details: str = Field(..., description="Detailed description of education alignment or shortcomings")
    skill_gaps: List[SkillGapItem] = Field(..., description="Categorized list of gap skills with importance, priority, and time estimate")
    summary: str = Field(..., description="General overview of career match findings")


# =====================================================================
# Engine 4: Career Enhancement Engine Models
# =====================================================================

class ResumeFlexBullet(BaseModel):
    original_bullet: str = Field(..., description="Original experience accomplishment bullet point")
    flexed_bullet: str = Field(..., description="Tailored experience accomplishment bullet point optimized for target role/JD")
    reasoning: str = Field(..., description="Strategy behind the adjustment (e.g. emphasizing metric outcomes, using specific keywords)")

class RoadmapMilestone(BaseModel):
    phase: str = Field(..., description="Phase sequence title (e.g. Phase 1: Core Toolsets)")
    skills: List[str] = Field(..., description="Skills focused on in this roadmap phase")
    topics: List[str] = Field(..., description="Detailed list of topics to study")
    estimated_time: str = Field(..., description="Expected duration (e.g. '2 weeks', '1 month')")
    resources: List[str] = Field(..., description="Recommended courses, documentation links, or books")

class CareerEnhancementSchema(BaseModel):
    resume_flex: List[ResumeFlexBullet] = Field(..., description="Optimized, high-impact bullet points customized for the job description")
    role_specific_rewrite_recommendations: List[str] = Field(..., description="General structure, layout, or ordering recommendations tailored for the role")
    learning_roadmap: List[RoadmapMilestone] = Field(..., description="Milestone-driven roadmap to bridge gaps and level up skills")
    cover_letter: str = Field(..., description="A professional, structured, high-converting cover letter customized to the JD and resume highlights")


# =====================================================================
# Engine 5: Interview Intelligence Engine Models
# =====================================================================

class InterviewQuestion(BaseModel):
    question: str = Field(..., description="The interview question")
    question_type: str = Field(..., description="Category: 'Technical', 'HR', 'Behavioral', 'Coding', 'Company-Specific'")
    difficulty: str = Field(..., description="Difficulty rating: 'Easy', 'Medium', 'Hard'")
    intent: str = Field(..., description="The interviewer's underlying intent behind the question")
    sample_answer: str = Field(..., description="Model answer or structure (e.g. STAR format for behavioral)")
    evaluation_criteria: List[str] = Field(..., description="Checklist items showing what the interviewer looks for in the answer")

class InterviewPrepSchema(BaseModel):
    questions: List[InterviewQuestion] = Field(..., description="Collection of generated interview questions and answers")


# =====================================================================
# Engine 6: Career Copilot Models
# =====================================================================

class NextStepItem(BaseModel):
    action: str = Field(..., description="Specific immediate task or action item")
    priority: str = Field(..., description="Action priority: 'High', 'Medium', 'Low'")
    rationale: str = Field(..., description="Reasoning behind prioritizing this action")

class CareerGuidanceReportSchema(BaseModel):
    career_advice: str = Field(..., description="High-level strategic guidance and feedback on professional direction")
    resume_improvements_summary: List[str] = Field(..., description="Aggregated summary of key updates required for the resume")
    salary_insights: str = Field(..., description="Salary market rate expectation based on skills, roles, and location")
    hiring_chances: int = Field(..., ge=0, le=100, description="Hiring probability estimate out of 100")
    next_steps: List[NextStepItem] = Field(..., description="Structured immediate next steps")
    study_suggestions: List[str] = Field(..., description="Recommended certifications, courses, or mini-projects to target")

class ChatMessage(BaseModel):
    role: str = Field(..., description="Role of message sender: 'user' or 'assistant'")
    content: str = Field(..., description="Message text content")

class ChatRequest(BaseModel):
    query: str = Field(..., description="The user query")
    res_id: Optional[str] = Field(None, description="Optional parsed resume database ID")


class ChatResponseSchema(BaseModel):
    response: str = Field(..., description="The conversational AI response")
    suggested_followups: List[str] = Field(..., description="Suggested follow-up questions to continue the guidance chat")


# =====================================================================
# Resume Analysis Engine Models (Direct Resume Review)
# =====================================================================

class ScoresBreakdown(BaseModel):
    grammar: int = Field(..., ge=0, le=100, description="Grammar and spelling score (0-100)")
    structure: int = Field(..., ge=0, le=100, description="Resume structure score (0-100)")
    formatting: int = Field(..., ge=0, le=100, description="Formatting and layout score (0-100)")
    content: int = Field(..., ge=0, le=100, description="Content quality and impact score (0-100)")
    ats: int = Field(..., ge=0, le=100, description="ATS compatibility score (0-100)")

class GrammarErrorDetail(BaseModel):
    section: str = Field(..., description="The section where the error was found")
    original_text: str = Field(..., description="The original text containing the error")
    error_type: str = Field(..., description="The type of error (e.g., Spelling, Punctuation, Tense)")
    explanation: str = Field(..., description="Explanation of why this is an error")
    suggested_correction: str = Field(..., description="Suggested correction")

class GrammarAnalysis(BaseModel):
    total_errors: int = Field(..., description="Total number of grammar/spelling errors found")
    errors: List[GrammarErrorDetail] = Field(default_factory=list, description="List of grammar and spelling errors")

class StructureAnalysis(BaseModel):
    missing_sections: List[str] = Field(default_factory=list, description="Missing standard sections")
    duplicate_sections: List[str] = Field(default_factory=list, description="Duplicate sections found")
    empty_sections: List[str] = Field(default_factory=list, description="Empty sections found")
    incorrect_order: List[str] = Field(default_factory=list, description="Incorrect section ordering issues")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations for structural improvements")

class FormattingAnalysis(BaseModel):
    issues: List[str] = Field(default_factory=list, description="Formatting issues found")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations for formatting improvements")

class ContentAnalysis(BaseModel):
    weak_statements: List[str] = Field(default_factory=list, description="Weak or passive statements in the resume")
    improved_versions: List[str] = Field(default_factory=list, description="Improved/rewritten versions of the weak statements")
    missing_information: List[str] = Field(default_factory=list, description="Missing information (e.g. metrics, dates, grades)")

class ATSAnalysisReport(BaseModel):
    ats_friendly: bool = Field(..., description="Whether the resume is ATS-friendly")
    issues: List[str] = Field(default_factory=list, description="ATS parsing or compatibility issues")

class SuggestionDetail(BaseModel):
    issue: str = Field(..., description="The identified issue")
    why_it_matters: str = Field(..., description="Why this issue affects success")
    recommended_fix: str = Field(..., description="Recommended fix")

class SuggestionsCategorized(BaseModel):
    high_priority: List[SuggestionDetail] = Field(default_factory=list, description="High priority improvement suggestions")
    medium_priority: List[SuggestionDetail] = Field(default_factory=list, description="Medium priority improvement suggestions")
    low_priority: List[SuggestionDetail] = Field(default_factory=list, description="Low priority improvement suggestions")

class ResumeAnalysisReportSchema(BaseModel):
    overall_score: int = Field(..., ge=0, le=100, description="Overall resume score out of 100")
    summary: str = Field(..., description="A short professional summary of the resume evaluation")
    scores: ScoresBreakdown = Field(..., description="Score breakdown across categories")
    grammar_analysis: GrammarAnalysis = Field(..., description="Detailed grammar and spelling analysis")
    structure_analysis: StructureAnalysis = Field(..., description="Detailed structure analysis")
    formatting_analysis: FormattingAnalysis = Field(..., description="Detailed formatting analysis")
    content_analysis: ContentAnalysis = Field(..., description="Detailed content quality analysis")
    ats_analysis: ATSAnalysisReport = Field(..., description="Detailed ATS compatibility analysis")
    strengths: List[str] = Field(default_factory=list, description="Strongest aspects of the resume")
    weaknesses: List[str] = Field(default_factory=list, description="Weaknesses in the resume")
    suggestions: SuggestionsCategorized = Field(..., description="Categorized actionable suggestions for improvement")

