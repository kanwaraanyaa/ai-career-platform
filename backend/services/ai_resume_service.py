import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
STABLE_MODEL = "gemini-3.1-flash-lite-preview"

def generate_latex_bullets(raw_notes: str, target_role: str):
    # We use a raw string (r""") to handle backslashes correctly
    # and double curly braces {{ }} to escape f-string interpolation
    prompt = f"""
    You are an expert technical resume writer. 
    Rewrite the following notes into 3 high-impact, professional bullet points for a {target_role} position.
    
    STRICT RULES:
    1. Output MUST start with \\begin{{itemize}} and end with \\end{{itemize}}.
    2. Use the 'Action Verb + Task + Result' framework.
    3. DO NOT include any markdown code blocks (```), backticks, or introductory text.
    4. Escape LaTeX special characters: change % to \\%, & to \\&, and $ to \\$.
    
    Example Output Format:
    \\begin{{itemize}}
      \\item Optimized backend API performance by implementing Redis caching, reducing latency by 40%.
      \\item Led a team of 4 developers to ship a real-time dashboard using React and Socket.io.
    \\end{{itemize}}

    User Notes: {raw_notes}
    """
    
    try:
        response = client.models.generate_content(
            model=STABLE_MODEL,
            contents=prompt
        )
        
        # Flash-lite is fast but might include surrounding text. We must isolate the itemize block.
        full_text = response.text.strip()
        
        # 1. Strip Markdown backticks if they exist
        if "```" in full_text:
            # Extract content between the first and last triple backticks
            full_text = full_text.split("```")[-2].replace("latex", "").strip()

        # 2. Final Guard: Ensure it starts with \begin{itemize}
        start_idx = full_text.find("\\begin{itemize}")
        end_idx = full_text.find("\\end{itemize}")
        
        if start_idx != -1 and end_idx != -1:
            return full_text[start_idx : end_idx + len("\\end{itemize}")]
        
        return full_text

    except Exception as e:
        print(f"Gemini API Error: {e}")
        # Fallback to a simple list so the LaTeX compiler doesn't break
        return f"\\begin{{itemize}} \\item {raw_notes} \\end{{itemize}}"