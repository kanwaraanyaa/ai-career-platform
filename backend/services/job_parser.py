# backend/services/job_parser.py
import os
import json
from google import genai  # Updated to modern client
from dotenv import load_dotenv

load_dotenv()

# Initialize the modern client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
STABLE_MODEL = "gemini-3.1-flash-lite-preview"

def extract_jd_data_with_llm(raw_jd_text: str):
    """Uses modern LLM client to extract standard skills from a messy job description."""
    
    prompt = f"""
    You are an expert technical recruiter. Read the following job description and extract the core required and preferred skills.
    
    Return ONLY valid JSON matching this exact structure:
    {{
      "job_title": "string",
      "required_skills": ["skill1", "skill2", "skill3"]
    }}

    RAW JOB DESCRIPTION:
    {raw_jd_text}
    """

    try:
        # Using the updated models.generate_content syntax
        response = client.models.generate_content(
            model=STABLE_MODEL,
            contents=prompt,
            config={
                'response_mime_type': 'application/json',
                'temperature': 0.1
            }
        )
        
        # Load the JSON from the response text
        parsed_data = json.loads(response.text)
        return parsed_data

    except Exception as e:
        print(f"JD Parsing Error: {e}")
        return {"error": "Failed to parse job description."}