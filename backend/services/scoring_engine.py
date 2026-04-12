import re
import json
from backend.services.resume_parser import get_gemini_response

def calculate_production_score(profile_data, match_score, jd_text):
    """
    Advanced Semantic Talent Intelligence Engine (Updated for Unbiased Capability Mining).
    Implements Global Tiering, Archetype Classification, and Dynamic Capability Scoring.
    """
    
    # --- 1. ARCHETYPE & PRESTIGE MINING (LLM Phase) ---
    prestige_prompt = f"""
    Act as a Global Talent Data Miner (2026 Standards). 
    Analyze the provided profile for technical depth, institutional prestige, and brand power.

    CONTEXT:
    PROFILE: {profile_data}
    CURRENT_JD_TARGET: {jd_text[:300]}

    INSTRUCTIONS:
    1. CLASSIFY ARCHETYPE: Is the candidate a 'Deep Researcher', 'System Architect', 'Data Specialist', or 'Product Engineer'? 
    2. INSTITUTIONAL TIERING: Identify if the university is Tier 1, 2, or 3.
    3. BRAND POWER: Rate prestige of companies/internships (Elite, Established, Local). 
    4. CAPABILITY SCORES (1-100): 
       - Design: Depth of system architecture, planning, or creative strategy.
       - Execution: Precision in implementation, coding, or data processing.
       - Research: Evidence of novel investigation, optimization, or academic publishing.
    5. SUCCESS SIGNALS: Extract 3 unique success signals from different sections: 1 from Professional Experience, 1 from Research/Patents, and 1 from Academic/Projects. Do NOT repeat the same company.
    6. EVIDENCE-BASED RECOMMENDATIONS: Identify 4 best-fit roles with quantified reasons.

    Return ONLY JSON:
    {{
        "archetype": "string",
        "institution_tier": 1 | 2 | 3,
        "brand_power_score": 1-100,
        "academic_score_raw": 1-100,
        "experience_score_raw": 1-100,
        "design_value": 1-100,
        "exec_value": 1-100,
        "research_value": 1-100,
        "design_label": "string",
        "exec_label": "string",
        "research_label": "string",
        "success_signals": ["Signal 1", "Signal 2", "Signal 3"],
        "recommendations": [
            {{ "role": "string", "reason": "string" }},
            {{ "role": "string", "reason": "string" }},
            {{ "role": "string", "reason": "string" }},
            {{ "role": "string", "reason": "string" }}
        ],
        "market_scarcity_insight": "string",
        "reasoning": "Data-driven summary."
    }}
    """
    
    try:
        raw_response = get_gemini_response(prestige_prompt)
        clean_json = re.sub(r"```json|```", "", raw_response).strip()
        llm_eval = json.loads(clean_json)
    except Exception as e:
        print(f"Mining Error: {e}")
        llm_eval = {
            "archetype": "Generalist", "institution_tier": 3, "brand_power_score": 50,
            "academic_score_raw": 60, "experience_score_raw": 60,
            "design_value": 70, "exec_value": 70, "research_value": 70,
            "design_label": "Standard", "exec_label": "Standard", "research_label": "Standard",
            "success_signals": ["Verified Technical Profile"], "recommendations": [],
            "market_scarcity_insight": "Stable profile.", "reasoning": "Baseline."
        }

    # --- 2. DYNAMIC PRESTIGE & SIGNAL BOOSTING ---
    education_text = str(profile_data.get('education', '')).lower()
    full_profile_text = (
        str(profile_data.get('experience', '')).lower() + 
        str(profile_data.get('projects', '')).lower() +
        str(profile_data.get('education', '')).lower() +
        str(profile_data.get('research', '')).lower()
    )
    
    # 2.1 Prestige Multipliers (Semantic Tiering)
    prestige_pts = 0
    tier = llm_eval.get("institution_tier", 3)
    if tier == 1: prestige_pts += 15 # Reward for Tier-1 (e.g., IIT, VIT, MIT) [cite: 84]
    elif tier == 2: prestige_pts += 7
    
    brand_bonus = (llm_eval.get("brand_power_score", 50) / 100) * 15
    prestige_pts += brand_bonus # Reward for Elite Brands (e.g., Deloitte, PwC, DRDL) [cite: 4, 8]

    # 2.2 Academic Contrast (GPA weighting)
    cgpa_match = re.search(r'(\d\.\d+)', education_text)
    cgpa = float(cgpa_match.group(1)) if cgpa_match else 0.0
    
    academic_pts = llm_eval.get("academic_score_raw", 60)
    if cgpa >= 9.0: 
        academic_pts += 15 # High-performer boost [cite: 25]
    elif 0 < cgpa < 7.5:
        academic_pts -= 15 # Contrast penalty for lower GPA

    # 2.3 Innovation Contrast (Research/Patent)
    innovation_keywords = ["ieee", "patent", "filed", "published", "journal", "research"]
    has_innovation = any(word in full_profile_text for word in innovation_keywords)

    if has_innovation:
        academic_pts += 10 # Massive differentiator for 2026 
    else:
        academic_pts -= 5 # Standard signal if missing research

    # --- 3. QUANTIFIED PROOF (Bigger Swings) ---
    proof_pts = 0
    gh = profile_data.get('github_stats', {})
    active_days = gh.get('activeDays', 0)
    
    if active_days > 40: 
        proof_pts += 20 # Reward for consistent production
    elif active_days < 5: 
        proof_pts -= 10 # Penalty for "Ghost" profiles
    
    if gh.get('stars', 0) > 10: 
        proof_pts += 15 # Social proof reward

    # --- 4. FINAL PRODUCTION FORMULA ---
    # Combine the new Unbiased Capability Average with traditional weighting
    capability_avg = (llm_eval.get("design_value", 70) + llm_eval.get("exec_value", 70) + llm_eval.get("research_value", 70)) / 3
    
    final_academic = min((academic_pts * 0.7) + (prestige_pts * 2), 100)
    final_experience = min(llm_eval.get("experience_score_raw", 60) + proof_pts, 100)
    weighted_score = (
        (match_score * 0.35) + 
        (final_academic * 0.20) + 
        (final_experience * 0.25) +
        (capability_avg * 0.20) # Integration of unbiased capability mining
    )

    return {
        "selection_probability": round(weighted_score),
        "prestige_insight": llm_eval.get("market_scarcity_insight"),
        "score_reasons": llm_eval.get("success_signals"),
        "archetype": llm_eval.get("archetype"),
        "recommendations": llm_eval.get("recommendations", []),
        "innovation_signal": has_innovation,
        "design_value": llm_eval.get("design_value"),
        "exec_value": llm_eval.get("exec_value"),
        "research_value": llm_eval.get("research_value"),
        "design_label": llm_eval.get("design_label"),
        "exec_label": llm_eval.get("exec_label"),
        "research_label": llm_eval.get("research_label"),
        "category": "Elite Candidate" if weighted_score > 90 else "Strong Fit" if weighted_score > 75 else "Potential"
    }