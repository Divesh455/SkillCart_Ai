import os
import json
import logging
from typing import Optional
from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker
import datetime

from app.core.config import settings

logger = logging.getLogger(__name__)

# Base class for SQLAlchemy models
Base = declarative_base()

class ResumeRecord(Base):
    __tablename__ = "resumes"

    res_id = Column(String(36), primary_key=True, index=True)
    name = Column(String(255), nullable=True)
    
    # Contact info columns
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    location = Column(String(255), nullable=True)
    linkedin = Column(String(255), nullable=True)
    github = Column(String(255), nullable=True)
    portfolio = Column(String(255), nullable=True)

    raw_text = Column(Text, nullable=True)
    parsed_json = Column(Text, nullable=True)  # JSON representation of ResumeSchema as backup
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class EducationRecord(Base):
    __tablename__ = "education"
    id = Column(Integer, primary_key=True, autoincrement=True)
    res_id = Column(String(36), ForeignKey("resumes.res_id", ondelete="CASCADE"), index=True)
    institution = Column(String(255), nullable=False)
    degree = Column(String(255), nullable=True)
    major = Column(String(255), nullable=True)
    start_date = Column(String(50), nullable=True)
    end_date = Column(String(50), nullable=True)
    gpa = Column(String(50), nullable=True)

class ExperienceRecord(Base):
    __tablename__ = "experience"
    id = Column(Integer, primary_key=True, autoincrement=True)
    res_id = Column(String(36), ForeignKey("resumes.res_id", ondelete="CASCADE"), index=True)
    company = Column(String(255), nullable=False)
    role = Column(String(255), nullable=False)
    start_date = Column(String(50), nullable=True)
    end_date = Column(String(50), nullable=True)
    highlights = Column(Text, nullable=True)  # JSON-encoded list of strings

class ProjectRecord(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, autoincrement=True)
    res_id = Column(String(36), ForeignKey("resumes.res_id", ondelete="CASCADE"), index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    highlights = Column(Text, nullable=True)  # JSON-encoded list of strings
    url = Column(String(255), nullable=True)

class SkillRecord(Base):
    __tablename__ = "skills"
    id = Column(Integer, primary_key=True, autoincrement=True)
    res_id = Column(String(36), ForeignKey("resumes.res_id", ondelete="CASCADE"), index=True)
    category = Column(String(255), nullable=False)
    skills = Column(Text, nullable=False)  # JSON-encoded list of strings

class CertificationRecord(Base):
    __tablename__ = "certifications"
    id = Column(Integer, primary_key=True, autoincrement=True)
    res_id = Column(String(36), ForeignKey("resumes.res_id", ondelete="CASCADE"), index=True)
    name = Column(String(255), nullable=False)
    issuer = Column(String(255), nullable=True)
    issue_date = Column(String(50), nullable=True)
    url = Column(String(255), nullable=True)

# Configure database engine
_engine = None
_SessionLocal = None

def get_engine():
    global _engine, _SessionLocal
    if _engine is not None:
        return _engine

    db_url = settings.DATABASE_URL
    if not db_url:
        raise ValueError("DATABASE_URL setting is not configured.")

    # Convert mysql:// to mysql+pymysql:// if driver is not specified
    if db_url.startswith("mysql://"):
        db_url = db_url.replace("mysql://", "mysql+pymysql://", 1)

    # Strip out ssl-mode or ssl_mode from the query params to prevent PyMySQL/SQLAlchemy TypeError
    if "?" in db_url:
        base_url, query_str = db_url.split("?", 1)
        params = query_str.split("&")
        filtered_params = [
            p for p in params 
            if not (p.startswith("ssl-mode=") or p.startswith("ssl_mode="))
        ]
        if filtered_params:
            db_url = base_url + "?" + "&".join(filtered_params)
        else:
            db_url = base_url

    connect_args = {}
    if "mysql" in db_url:
        # Enable SSL connection for MySQL (e.g. Aiven)
        connect_args["ssl"] = {"ssl_mode": "REQUIRED"}

    _engine = create_engine(
        db_url,
        connect_args=connect_args,
        pool_pre_ping=True,
        pool_recycle=3600
    )
    _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    return _engine

def init_db() -> None:
    """Initialize the database schema, creating tables if they do not exist."""
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized successfully.")

def get_db_session():
    """Context manager / generator to get a DB session."""
    get_engine()  # Ensure engine and sessionmaker are initialized
    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()

def save_resume_data(res_id: str, name: str, raw_text: str, parsed_data: dict) -> None:
    """Helper function to save parsed resume data into the database."""
    get_engine()  # Ensure initialized
    session = _SessionLocal()
    try:
        record = session.query(ResumeRecord).filter(ResumeRecord.res_id == res_id).first()
        if not record:
            record = ResumeRecord(res_id=res_id)
            session.add(record)
        
        record.name = name
        record.raw_text = raw_text
        record.parsed_json = json.dumps(parsed_data)
        record.created_at = datetime.datetime.utcnow()
        
        # Save contact details
        contact = parsed_data.get("contact", {})
        if contact:
            record.email = contact.get("email")
            record.phone = contact.get("phone")
            record.location = contact.get("location")
            record.linkedin = contact.get("linkedin")
            record.github = contact.get("github")
            record.portfolio = contact.get("portfolio")
        
        # Flush parent record first to ensure it exists in DB (satisfying FK constraints for child tables)
        session.flush()
        
        # Clear existing related records for idempotency (e.g. if the user parses/updates the same resume ID)
        session.query(EducationRecord).filter(EducationRecord.res_id == res_id).delete()
        session.query(ExperienceRecord).filter(ExperienceRecord.res_id == res_id).delete()
        session.query(ProjectRecord).filter(ProjectRecord.res_id == res_id).delete()
        session.query(SkillRecord).filter(SkillRecord.res_id == res_id).delete()
        session.query(CertificationRecord).filter(CertificationRecord.res_id == res_id).delete()
        
        # Save education
        education_list = parsed_data.get("education", [])
        for edu in education_list:
            edu_rec = EducationRecord(
                res_id=res_id,
                institution=edu.get("institution") or "",
                degree=edu.get("degree"),
                major=edu.get("major"),
                start_date=edu.get("start_date"),
                end_date=edu.get("end_date"),
                gpa=edu.get("gpa")
            )
            session.add(edu_rec)
            
        # Save experience
        experience_list = parsed_data.get("experience", [])
        for exp in experience_list:
            exp_rec = ExperienceRecord(
                res_id=res_id,
                company=exp.get("company") or "",
                role=exp.get("role") or "",
                start_date=exp.get("start_date"),
                end_date=exp.get("end_date"),
                highlights=json.dumps(exp.get("highlights", []))
            )
            session.add(exp_rec)
            
        # Save projects
        project_list = parsed_data.get("projects", [])
        for proj in project_list:
            proj_rec = ProjectRecord(
                res_id=res_id,
                name=proj.get("name") or "",
                description=proj.get("description") or "",
                highlights=json.dumps(proj.get("highlights", [])),
                url=proj.get("url")
            )
            session.add(proj_rec)
            
        # Save skills
        skill_list = parsed_data.get("skills", [])
        for skill in skill_list:
            skill_rec = SkillRecord(
                res_id=res_id,
                category=skill.get("category") or "",
                skills=json.dumps(skill.get("skills", []))
            )
            session.add(skill_rec)
            
        # Save certifications
        cert_list = parsed_data.get("certifications", [])
        for cert in cert_list:
            cert_rec = CertificationRecord(
                res_id=res_id,
                name=cert.get("name") or "",
                issuer=cert.get("issuer"),
                issue_date=cert.get("issue_date"),
                url=cert.get("url")
            )
            session.add(cert_rec)
            
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to save resume {res_id}: {e}")
        raise e
    finally:
        session.close()

def get_resume_data(res_id: str) -> Optional[dict]:
    """Helper function to retrieve parsed resume data from the database."""
    get_engine()  # Ensure initialized
    session = _SessionLocal()
    try:
        record = session.query(ResumeRecord).filter(ResumeRecord.res_id == res_id).first()
        if not record:
            return None
        
        # Build contact info
        contact = {
            "email": record.email,
            "phone": record.phone,
            "location": record.location,
            "linkedin": record.linkedin,
            "github": record.github,
            "portfolio": record.portfolio
        }
        
        # Build education list
        education = []
        edu_recs = session.query(EducationRecord).filter(EducationRecord.res_id == res_id).all()
        for edu in edu_recs:
            education.append({
                "institution": edu.institution,
                "degree": edu.degree,
                "major": edu.major,
                "start_date": edu.start_date,
                "end_date": edu.end_date,
                "gpa": edu.gpa
            })
            
        # Build experience list
        experience = []
        exp_recs = session.query(ExperienceRecord).filter(ExperienceRecord.res_id == res_id).all()
        for exp in exp_recs:
            highlights = []
            if exp.highlights:
                try:
                    highlights = json.loads(exp.highlights)
                except Exception:
                    highlights = []
            experience.append({
                "company": exp.company,
                "role": exp.role,
                "start_date": exp.start_date,
                "end_date": exp.end_date,
                "highlights": highlights
            })
            
        # Build projects list
        projects = []
        proj_recs = session.query(ProjectRecord).filter(ProjectRecord.res_id == res_id).all()
        for proj in proj_recs:
            highlights = []
            if proj.highlights:
                try:
                    highlights = json.loads(proj.highlights)
                except Exception:
                    highlights = []
            projects.append({
                "name": proj.name,
                "description": proj.description,
                "highlights": highlights,
                "url": proj.url
            })
            
        # Build skills list
        skills = []
        skill_recs = session.query(SkillRecord).filter(SkillRecord.res_id == res_id).all()
        for sk in skill_recs:
            skill_list = []
            if sk.skills:
                try:
                    skill_list = json.loads(sk.skills)
                except Exception:
                    skill_list = []
            skills.append({
                "category": sk.category,
                "skills": skill_list
            })
            
        # Build certifications list
        certifications = []
        cert_recs = session.query(CertificationRecord).filter(CertificationRecord.res_id == res_id).all()
        for cert in cert_recs:
            certifications.append({
                "name": cert.name,
                "issuer": cert.issuer,
                "issue_date": cert.issue_date,
                "url": cert.url
            })
            
        # Compile ResumeSchema compatible dict
        return {
            "res_id": record.res_id,
            "name": record.name,
            "contact": contact,
            "education": education,
            "experience": experience,
            "projects": projects,
            "skills": skills,
            "certifications": certifications
        }
    except Exception as e:
        logger.error(f"Failed to get resume {res_id}: {e}")
        return None
    finally:
        session.close()
