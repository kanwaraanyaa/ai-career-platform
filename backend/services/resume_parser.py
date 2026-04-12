import os
import json
import re
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
STABLE_MODEL = "gemini-3.1-flash-lite-preview"

def extract_full_profile_intelligence(raw_text: str, external_metadata=None):
    prompt = f"""
    Act as an Unbiased Global Talent Intelligence System. 
    Analyze the provided resume and metadata to extract facts and perform 2026 market mining.

    STRICT EXTRACTION RULES:
    - PROFESSIONAL EXPERIENCE: Only extract entries that are formal Jobs or Internships. If the candidate is a student with no formal work history (only projects), return "experience": [].
    - RESEARCH & PATENTS: Do NOT put these in the projects list. Extract them into the dedicated "research_and_patents" array. 
    - DEEP SKILL MINING: Scan project descriptions and research summaries for technical keywords (e.g., OAuth2, DynamoDB, MediaPipe, Flask) and include them in "skills_list". [cite: 10, 11, 18, 19]
    - ZERO HALLUCINATION: If a data point (like a GPA or a Job) is not explicitly in the text, return "N/A". Never assume a value.

    RAW TEXT: 
    {raw_text}

    METADATA (External Verification): 
    {external_metadata}

    TASK LIST:
    1. FACTUAL EXTRACTION: Capture Name, Skills, Education, Experience, and Research/Projects. [cite: 1, 25, 32]
    2. ARCHETYPE DISCOVERY: Analyze evidence density. Assign a title based on the primary domain of impact (e.g., 'Backend Architect', 'AI Research Engineer').
    3. EXCELLENCE MINING: Identify 3 objective "Signals of Excellence" (Patents, Certifications, high-impact KPIs). 
    4. 2026 MARKET SCARCITY: Analyze how rare this specific professional combination is (e.g., Java Systems + AI Audio). 
    5. EXPLAINABLE SCORING (EVALUATION FACTORS): Identify the top 4 objective factors from the resume that determined the final "strength_score". Base these ONLY on the available data. Factors can include academic standing, project complexity, technical skill density, publication record, or experience volume (or lack thereof). If a metric like GPA or experience is missing, evaluate based on what IS present (e.g., density of personal projects). Do NOT label them as strengths or weaknesses. Just state the neutral factor and the concrete evidence found.
    6. EDUCATION CHRONOLOGY: Extract ONLY the 4-digit graduation or expected graduation year for each degree. If a date range is provided, extract ONLY the final completion year. Sort the education array chronologically from oldest to newest, ensuring the highest/most recent degree (prioritizing University/College over High School) is the LAST item in the list. If no year is found, set "year" to "Unknown".
    7. DYNAMIC COMPETENCY MAPPING: 
       - Identify the 5 most critical technical domains found in THIS specific resume.
       - Assign a score (1-100) based on project impact evidence.
       - Return as "skill_dna": [{{"subject": "Name", "A": score}}].

    OUTPUT JSON FORMAT:
    {{
      "name": "string",
      "skills_list": [],
      "education": [{{
          "degree": "string", 
          "institution": "string", 
          "year": "string", 
          "gpa": "string or N/A"
      }}],
      "experience": [{{
          "role": "string", 
          "company": "string", 
          "duration": "string",
          "impact": "string"
      }}],
      "research_and_patents": [{{
          "type": "Patent" or "Publication",
          "title": "string", 
          "summary": "string",
          "year": "string"
      }}],
      "projects": [{{
          "title": "string", 
          "summary": "string",
          "technologies": []
      }}],
      "analytics": {{
          "archetype": "string",
          "strength_score": 1-100,
          "evaluation_factors": [
             {{ "factor": "string", "evidence": "string" }},
             {{ "factor": "string", "evidence": "string" }},
             {{ "factor": "string", "evidence": "string" }},
             {{ "factor": "string", "evidence": "string" }}
          ],
          "skill_dna": [
            {{ "subject": "string", "A": 1-100 }},
            {{ "subject": "string", "A": 1-100 }},
            {{ "subject": "string", "A": 1-100 }},
            {{ "subject": "string", "A": 1-100 }},
            {{ "subject": "string", "A": 1-100 }}
          ],
          "success_signals": [],
          "market_insight": "string",
          "recommended_roles": [] 
      }},
      "total_experience": "string"
    }}
    """

    try:
        response = client.models.generate_content(
            model=STABLE_MODEL,
            contents=prompt,
            config={
                'response_mime_type': 'application/json',
                'temperature': 0.1
            }
        )
        
        # Clean up code blocks if returned
        clean_json = re.sub(r"```json|```", "", response.text).strip()
        return json.loads(clean_json)

    except Exception as e:
        print(f"Super Prompt Intelligence Error: {e}")
        return {
            "error": str(e),
            "analytics": {
                "archetype": "Generalist",
                "strength_score": 60,
                "skill_dna": [
                    {"subject": "Core Skills", "A": 60},
                    {"subject": "Execution", "A": 60},
                    {"subject": "Strategy", "A": 60},
                    {"subject": "Communication", "A": 60},
                    {"subject": "Adaptability", "A": 60}
                ],
                "success_signals": ["Verified Technical Foundation"],
                "market_insight": "Standard profile signal detected.",
                "category": "Potential"
            }
        }

def get_gemini_response(prompt: str):
    """Helper for JD matching and secondary analysis."""
    try:
        response = client.models.generate_content(
            model=STABLE_MODEL,
            contents=prompt,
        )
        return response.text
    except Exception as e:
        print(f"Gemini Response Error: {e}")
        return ""