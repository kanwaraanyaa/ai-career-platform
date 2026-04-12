import re

# --- ADD THIS FUNCTION (MISSING FROM YOUR CODE) ---
def calculate_ats_score(resume_corpus, jd_skills):
    """
    Calculates a keyword-based ATS score by checking how many JD skills 
    appear in the full resume text.
    """
    if not jd_skills:
        return 0, []

    found_keywords = []
    resume_text_lower = resume_corpus.lower()

    for skill in jd_skills:
        # Using regex to find whole words only (prevents 'Java' matching 'Javascript')
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, resume_text_lower):
            found_keywords.append(skill)

    score = (len(found_keywords) / len(jd_skills)) * 100
    return round(score, 2), found_keywords

# --- KEEP YOUR EXISTING FUNCTION BELOW ---
def generate_evidence_report(request_data, ats_results):
    experience_text = request_data.get("experience", "")
    education_text = request_data.get("education", "")
    
    # We use .get() safely to prevent KeyErrors
    found_skills = [s.lower() for s in ats_results.get("found_keywords", [])]
    # In analysis.py, you aren't passing 'all_jd_skills', so we default to found_skills 
    # or you can update the call in analysis.py
    jd_skills = [s.lower() for s in ats_results.get("all_jd_skills", found_skills)] 
    
    gpa_match = re.search(r"(?:gpa|cgpa|pointer|aggregate)\s*[:\-]?\s*(\d+\.\d+)", education_text.lower())
    gpa_val = gpa_match.group(1) if gpa_match else "Not Detected"
    
    org_matches = re.findall(r"([A-Z][a-z]+(?:\s[A-Z][a-z]+)+)", experience_text)
    primary_org = org_matches[0] if org_matches else "Independent"

    missing_skills = [s for s in jd_skills if s not in found_skills]
    critical_gaps = missing_skills[:3]
    
    denominator = len(jd_skills) if len(jd_skills) > 0 else 1
    penalty_per_skill = 100 / denominator
    total_penalty = len(missing_skills) * penalty_per_skill

    strengths = []
    if gpa_val != "Not Detected":
        strengths.append(f"Academic Record: {gpa_val} Verified")
    if primary_org != "Independent":
        strengths.append(f"Industry Exposure at {primary_org}")
    
    metrics = re.findall(r"(\d+%\s\w+|\d+\+?\s?records|\d+\+?\s?users)", experience_text.lower())
    for m in metrics[:2]:
        strengths.append(f"Quantified Impact: {m}")

    return {
    "prestige_audit": {
        "institution_found": "Detected" if gpa_val != "Not Detected" else "Incomplete",
        "primary_organization": str(primary_org) if primary_org else "Independent",
        "research_indicator": "Found in Text" if "journal" in education_text.lower() or "publication" in education_text.lower() else "None Detected"
    },
    "ats_impact_report": {
        "score": ats_results.get('ats_score', 0),
        "calculated_penalty": f"-{round(total_penalty, 1)}%",
        "top_missing_skills": critical_gaps
    },
    "strategic_points": {
        "verified_strengths": strengths if strengths else ["Profile Analyzed"],
        "detected_gaps": [f"Missing literal match for {s}" for s in critical_gaps]
    }
}