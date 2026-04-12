from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import re

# Internal Service Imports
from backend.services.job_parser import extract_jd_data_with_llm
from backend.services.matcher import detect_skill_gap
from backend.services.scoring_engine import calculate_production_score
from backend.services.ats_engine import calculate_ats_score
from backend.services.report_generator import ReportGenerator

# Initialize the Router
router = APIRouter()

# Data Model for the Request
class GapAnalysisRequest(BaseModel):
    resume_skills: list[str]
    jd_text: str
    education_text: str
    experience_text: str
    github_stats: dict
    coding_stats: dict | None = None

@router.post("/analyze-gap/")
async def analyze_job_gap(request: GapAnalysisRequest):
    # 1. Extract JD Intelligence
    jd_data = extract_jd_data_with_llm(request.jd_text)
    if "error" in jd_data:
        raise HTTPException(status_code=400, detail="Could not parse JD.")
        
    jd_skills = jd_data.get("required_skills", [])
    job_title = jd_data.get("job_title", "Target Role")

    # 2. Score Calculations (ATS & Semantic Match)
    full_resume_corpus = f"{' '.join(request.resume_skills)} {request.experience_text} {request.education_text}"
    ats_score, found_keywords = calculate_ats_score(full_resume_corpus, jd_skills)
    
    resume_context_pool = request.resume_skills + \
                         [s.strip() for s in request.experience_text.split(".") if len(s.strip()) > 10] + \
                         [s.strip() for s in request.education_text.split(".") if len(s.strip()) > 10]

    analysis_results = detect_skill_gap(resume_context_pool, jd_skills)

    final_report = calculate_production_score(
        profile_data={
            "education": request.education_text, 
            "experience": request.experience_text, 
            "github_stats": request.github_stats, 
            "coding_stats": request.coding_stats
        },
        match_score=analysis_results["match_score"],
        jd_text=request.jd_text
    )

    # --- 3. UNBIASED DYNAMIC EXTRACTION ---
    gpa_match = re.search(r"(\d+\.\d+)", request.education_text)
    extracted_gpa = gpa_match.group(1) if gpa_match else "N/A"

    # --- THE FIX: Handle "Foundational" Experience Properly ---
    is_foundational = request.experience_text.strip().lower() == "foundational"

    if is_foundational:
        experience_details = [] # Correctly sends 0 internships to the generator
    else:
        company_match = re.search(r"at ([\w\s&]+) \(", request.experience_text)
        extracted_company = company_match.group(1).strip() if company_match else "Enterprise"
        experience_details = [{"company": extracted_company}]

    project_match = re.search(r"^([^:\n]+)", request.experience_text if not is_foundational else "Deep Packet Inspection Engine")
    extracted_project = project_match.group(1).strip() if project_match else "Primary Development Project"

    # --- 4. DATA SYNC ---
    report_profile = {
        "experience_details": experience_details, # Now correctly passes an empty list
        "education": request.education_text,
        "gpa": extracted_gpa,
        "projects": [{"title": extracted_project}],
        # Broadened to catch your Patent and IEEE Research
        "research": True if "Publication" in request.education_text or "Patent" in request.education_text or "IEEE" in request.experience_text else False
    }

    combined_gap_data = {
        **analysis_results,
        "github_stats": request.github_stats,
        "coding_stats": request.coding_stats,
        "detailed_strengths": final_report.get("analytics", {}).get("evaluation_factors", [])
    }

    evidence_audit = ReportGenerator.generate_dossier(report_profile, combined_gap_data)

    return {
        "job_title": job_title,
        "ats_score": ats_score,
        "ats_found_keywords": found_keywords,
        "semantic_match_score": analysis_results["match_score"],
        "selection_probability": final_report.get("selection_probability", 0),
        "prestige_insight": final_report.get("prestige_insight", ""),
        "archetype": final_report.get("archetype", "Specialist"),
        "recommendations": final_report.get("recommendations", []),
        "matched_skills": analysis_results["matched_skills"],
        "missing_skills": analysis_results["missing_skills"],
        "evidence_audit": evidence_audit,
        "message": "Analysis successful.",
        "evaluation_factors": final_report.get("analytics", {}).get("evaluation_factors", [])
    }