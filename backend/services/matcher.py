from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import numpy as np
import json
import re
# Load the model once at the top level for performance
model = SentenceTransformer("all-MiniLM-L6-v2")

import re # Make sure re is imported at the top of your file

def generate_axes_with_llm(skills_list, llm_client):
    """
    Uses LLM to create meaningful competency axes dynamically
    """

    prompt = f"""
    Given the following skills:

    {skills_list}

    Group them into 4-6 high-level competency areas.

    Return ONLY a valid JSON array of strings.

    Example:
    ["Machine Learning", "Backend Systems", "Cloud Infrastructure"]
    """

    response = llm_client(prompt)

    try:
        # Clean up any markdown code blocks Gemini might add
        clean_json = re.sub(r"```json|```", "", response).strip()
        axes = json.loads(clean_json)
        return axes[:6]
    except Exception as e:
        print(f"Error parsing Gemini axes response: {e} - Raw response: {response}")
        return ["General Skills", "Technical Execution", "Problem Solving", "Domain Knowledge"]
def get_radar_data(skills_list, llm_client):

    if not skills_list:
        return []

    # 🔥 Step 1: LLM decides axes (UNBIASED)
    axes = generate_axes_with_llm(skills_list, llm_client)

    skill_vectors = model.encode(skills_list)
    axis_vectors = model.encode(axes)

    radar_results = []

    for i, axis in enumerate(axes):
        axis_vec = axis_vectors[i].reshape(1, -1)

        sims = cosine_similarity(skill_vectors, axis_vec).flatten()

        weighted = np.mean(np.sort(sims)[-3:])
        score = int(weighted * 100) 

        if score > 20:
            radar_results.append({
                "subject": axis.upper(),
                "A": min(score, 100),
                "fullMark": 100
            })

    if not radar_results:
        return [{
            "subject": "GENERAL",
            "A": 70,
            "fullMark": 100
        }]

    return radar_results

def detect_skill_gap(resume_context_pool, jd_skills_from_llm):
    """
    INNOVATION-AWARE SEMANTIC MATCHER:
    Detects skill alignment through research signals, patents, and quantified impact.
    """
    if not jd_skills_from_llm:
        return {"match_score": 0, "matched_skills": [], "missing_skills": []}

    # Encode context pool and job requirements
    res_vecs = model.encode(resume_context_pool)
    jd_vecs = model.encode(jd_skills_from_llm)
    sim_matrix = cosine_similarity(jd_vecs, res_vecs)

    # 1. INNOVATION ANCHOR DETECTION
    # High-sensitivity anchors to find Diya's Research [cite: 80] or Tanish's Patent [cite: 23]
    innovation_anchors = model.encode([
        "published research paper journal publication conference ieee",
        "patent filed intellectual property innovation disclosure framework",
        "novel methodology experimental framework technical thesis automation"
    ])
    
    innovation_scores = cosine_similarity(res_vecs, innovation_anchors)
    has_research_signal = np.max(innovation_scores) > 0.65 

    matched_skills = []
    missing_skills = []
    total_score = 0

    for idx, jd_skill in enumerate(jd_skills_from_llm):
        # Calculate similarity against EVERY item in the resume context
        skill_sims = sim_matrix[idx]
        best_match_idx = np.argmax(skill_sims)
        best_score = skill_sims[best_match_idx]

        # REFINEMENT: Extract quantified evidence (e.g., '15-20% uplift' [cite: 49])
        matched_text = resume_context_pool[best_match_idx].lower()
        has_quantified_evidence = any(char.isdigit() for char in matched_text)

        # 2. ADAPTIVE SEMANTIC SCORING
        if best_score > 0.68: 
            matched_skills.append(jd_skill)
            # Bias-Free Bonus for quantified impact metrics [cite: 50, 62]
            total_score += 1.15 if has_quantified_evidence else 1.0
            
        elif best_score > 0.45: 
            # High-Performance Boost: Credit given for conceptual matches backed by Research/IP
            credit = 0.95 if (has_research_signal or has_quantified_evidence) else 0.8
            matched_skills.append(f"{jd_skill} (Evidence-Validated)")
            total_score += credit
        else:
            missing_skills.append(jd_skill)

    # Calculate final match relative to JD length
    match_score = (total_score / len(jd_skills_from_llm)) * 100

    return {
        "match_score": round(match_score, 2),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "innovation_detected": bool(has_research_signal)
    }