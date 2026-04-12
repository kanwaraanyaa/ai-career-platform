from fastapi import APIRouter, UploadFile, File, Form
import shutil
import re

from backend.utils.pdf_reader import extract_resume_text
from backend.services.resume_parser import extract_full_profile_intelligence
from backend.services.github_analyzer import analyze_github_profile
from backend.services.coding_analyzer import analyze_coding_profile
from backend.services.linkedin_analyzer import analyze_linkedin_profile
from backend.services.matcher import get_radar_data
from backend.services.scoring_engine import calculate_production_score
from backend.services.resume_parser import get_gemini_response
from backend.services.report_generator import ReportGenerator

router = APIRouter()
UPLOAD_FOLDER = "backend/uploads"

@router.post("/upload_resume/")
async def upload_resume(
    file: UploadFile = File(...),
    github_url: str = Form(None),
    coding_url: str = Form(None),
    linkedin_url: str = Form(None)
):
    file_location = f"{UPLOAD_FOLDER}/{file.filename}"

    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    raw_text = extract_resume_text(file_location)
    cleaned_text = re.sub(r"[♦•▪■❖\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]", " ", raw_text)

    # --- 1. EXTERNAL VERIFICATION ---
    github_data = {"languages": [], "repos": 0, "stars": 0, "activeDays": 0}
    if github_url:
        gh_data = analyze_github_profile(github_url)
        if gh_data and "error" not in gh_data:
            github_data = {
                "languages": gh_data.get("verified_languages", []),
                "repos": gh_data.get("public_repos", 0),
                "stars": gh_data.get("total_stars", 0),
                "activeDays": gh_data.get("recent_active_days", 0)
            }

    coding_stats = analyze_coding_profile(coding_url) if coding_url else None
    linkedin_stats = analyze_linkedin_profile(linkedin_url) if linkedin_url else None

    # --- 2. AI INTELLIGENCE ---
    full_intelligence = extract_full_profile_intelligence(cleaned_text, github_data)

    if "error" in full_intelligence:
        return {"filename": file.filename, "message": "AI Intelligence failed.", "error": full_intelligence["error"]}

    # --- 3. FORMATTING DATA FOR THE SCORER ---
    edu_list = full_intelligence.get("education", [])
    formatted_edu = "\n".join([f"{e.get('degree')} from {e.get('institution')} ({e.get('year')})" for e in edu_list])

    exp_list = full_intelligence.get("experience", [])
    formatted_exp = "\n\n".join([f"{e.get('role')} at {e.get('company')} ({e.get('duration')}): {e.get('impact')}" for e in exp_list]) if exp_list else "Foundational"

    proj_list = full_intelligence.get("projects", [])
    formatted_proj = "\n\n".join([f"{p.get('title')}: {p.get('summary')}" for p in proj_list])

    res_list = full_intelligence.get("research_and_patents", [])
    formatted_res = "\n\n".join([f"[{r.get('type')}] {r.get('title')} ({r.get('year')}):\n{r.get('summary')}" for r in res_list])

    # --- 4. CALCULATE DYNAMIC SCORING (Breaks the "88" Score) ---
    initial_profile = {
        "education": formatted_edu,
        "experience": formatted_exp,
        "projects": formatted_proj,
        "research": formatted_res,
        "github_stats": github_data
    }
    raw_skills = full_intelligence.get("skills_list", [])
    github_langs = github_data.get("languages", [])
    
    unified_skills = list(dict.fromkeys(raw_skills + github_langs))
    unified_skills = [s.lower().strip() for s in unified_skills if len(s) > 2]
    # We use a neutral match score of 75 for the initial "Global" dashboard view
    initial_scorer_results = calculate_production_score(initial_profile, 75, "")

    # --- 4.5 GENERATE UNBIASED DOSSIER DATA ---
    # This pulls directly from the resume we just parsed
    evidence_audit = ReportGenerator.generate_dossier(
        parsed_resume={
            "education": formatted_edu,
            "gpa": full_intelligence.get("gpa", "N/A"), # Ensure your parser extracts this
            "experience_details": exp_list, # The raw list of company objects
            "projects": proj_list,
            "research": res_list
        },
        gap_data=initial_scorer_results
    )

    # --- 5. FINAL JSON RETURN ---
    return {
        "filename": file.filename,
        "name": full_intelligence.get("name", ""),
        "skills_list": unified_skills, # Use the unified list for consistency
        "github_repos": github_data.get("repos", 0),
        "github_stars": github_data.get("stars", 0),
        "github_active_days": github_data.get("activeDays", 0),
        "github_skills": github_langs,
        "coding_stats": coding_stats,
        "linkedin_stats": linkedin_stats,
        "experience": formatted_exp, 
        "projects": formatted_proj,
        "education": formatted_edu,
        "research": formatted_res,
        "total_experience": full_intelligence.get("total_experience", "Foundational"),
        "selection_probability": initial_scorer_results["selection_probability"],
        "evidence_audit": evidence_audit,
        "prestige_insight": initial_scorer_results["prestige_insight"],
        "archetype": initial_scorer_results["archetype"],
        "recommendations": initial_scorer_results["recommendations"],
        
        "evaluationFactors": full_intelligence.get("analytics", {}).get("evaluation_factors", []),
        "scoreReasons": initial_scorer_results.get("score_reasons", []),
        # --- CRITICAL KEYS: These link to Dashboard.tsx progress bars ---
        "designValue": initial_scorer_results.get("design_value", 70),
        "execValue": initial_scorer_results.get("exec_value", 70),
        "researchValue": initial_scorer_results.get("research_value", 70),
        "designScore": initial_scorer_results.get("design_label", "Standard"),
        "execScore": initial_scorer_results.get("exec_label", "Standard"),
        "researchScore": initial_scorer_results.get("research_label", "Standard"),

        "analytics": {
            # Fixes the 'single line' bug by using the full skill pool
            "skill_dna": get_radar_data(unified_skills, get_gemini_response),
            "success_signals": initial_scorer_results["score_reasons"],
            "evaluation_factors": full_intelligence.get("analytics", {}).get("evaluation_factors", [])
        }
    }