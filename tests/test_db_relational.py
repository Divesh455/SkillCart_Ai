import pytest
from unittest.mock import patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Override database URL to use an in-memory SQLite database for testing
settings.DATABASE_URL = "sqlite:///:memory:"

from app.core.db import (
    Base,
    init_db,
    save_resume_data,
    get_resume_data,
    ResumeRecord,
    EducationRecord,
    ExperienceRecord,
    ProjectRecord,
    SkillRecord,
    CertificationRecord,
    get_engine,
    _SessionLocal
)

@pytest.fixture(autouse=True)
def setup_test_db():
    # Make sure we re-initialize the in-memory db engine for each test
    import app.core.db as db_module
    
    # Re-create engine with sqlite memory URL
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    db_module._engine = engine
    db_module._SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    yield
    # Clean up
    Base.metadata.drop_all(bind=engine)

def test_save_and_retrieve_relational_resume_data():
    dummy_res_id = "test-uuid-12345"
    dummy_name = "Jane Doe"
    dummy_raw_text = "Jane Doe's raw resume content"
    
    dummy_parsed_data = {
        "res_id": dummy_res_id,
        "name": dummy_name,
        "contact": {
            "email": "jane@example.com",
            "phone": "555-0199",
            "location": "San Francisco, CA",
            "linkedin": "linkedin.com/in/janedoe",
            "github": "github.com/janedoe",
            "portfolio": "janedoe.me"
        },
        "education": [
            {
                "institution": "Stanford University",
                "degree": "MS",
                "major": "Computer Science",
                "start_date": "2020",
                "end_date": "2022",
                "gpa": "3.9"
            }
        ],
        "experience": [
            {
                "company": "Tech Corp",
                "role": "Software Engineer",
                "start_date": "2022-06",
                "end_date": "Present",
                "highlights": ["Developed microservices", "Improved database performance"]
            }
        ],
        "projects": [
            {
                "name": "SkillCart AI",
                "description": "AI-powered resume optimizer backend",
                "highlights": ["Utilized FastAPI and LLMs", "Designed database schema"],
                "url": "github.com/techcorp/skillcart"
            }
        ],
        "skills": [
            {
                "category": "Programming Languages",
                "skills": ["Python", "JavaScript", "SQL"]
            }
        ],
        "certifications": [
            {
                "name": "AWS Certified Solutions Architect",
                "issuer": "Amazon Web Services",
                "issue_date": "2023-01",
                "url": "aws.amazon.com/credentials/123"
            }
        ]
    }
    
    # Save the data
    save_resume_data(
        res_id=dummy_res_id,
        name=dummy_name,
        raw_text=dummy_raw_text,
        parsed_data=dummy_parsed_data
    )
    
    # Retrieve the data
    retrieved = get_resume_data(dummy_res_id)
    
    assert retrieved is not None
    assert retrieved["res_id"] == dummy_res_id
    assert retrieved["name"] == dummy_name
    
    # Verify contact
    assert retrieved["contact"]["email"] == "jane@example.com"
    assert retrieved["contact"]["portfolio"] == "janedoe.me"
    
    # Verify education
    assert len(retrieved["education"]) == 1
    assert retrieved["education"][0]["institution"] == "Stanford University"
    assert retrieved["education"][0]["degree"] == "MS"
    
    # Verify experience
    assert len(retrieved["experience"]) == 1
    assert retrieved["experience"][0]["company"] == "Tech Corp"
    assert "Developed microservices" in retrieved["experience"][0]["highlights"]
    
    # Verify projects
    assert len(retrieved["projects"]) == 1
    assert retrieved["projects"][0]["name"] == "SkillCart AI"
    assert "Utilized FastAPI and LLMs" in retrieved["projects"][0]["highlights"]
    
    # Verify skills
    assert len(retrieved["skills"]) == 1
    assert retrieved["skills"][0]["category"] == "Programming Languages"
    assert "Python" in retrieved["skills"][0]["skills"]
    
    # Verify certifications
    assert len(retrieved["certifications"]) == 1
    assert retrieved["certifications"][0]["name"] == "AWS Certified Solutions Architect"
    assert retrieved["certifications"][0]["issuer"] == "Amazon Web Services"

def test_idempotent_save():
    dummy_res_id = "test-uuid-5678"
    dummy_name = "Jane Doe"
    
    # Save once
    save_resume_data(
        res_id=dummy_res_id,
        name=dummy_name,
        raw_text="Initial text",
        parsed_data={"education": [{"institution": "College A"}]}
    )
    
    # Save again (update)
    save_resume_data(
        res_id=dummy_res_id,
        name=dummy_name,
        raw_text="Updated text",
        parsed_data={"education": [{"institution": "University B"}]}
    )
    
    retrieved = get_resume_data(dummy_res_id)
    assert retrieved is not None
    # Should only contain University B, and College A must be cleared
    assert len(retrieved["education"]) == 1
    assert retrieved["education"][0]["institution"] == "University B"
