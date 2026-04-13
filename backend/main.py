from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from routes import upload, analysis, resume
# Import the service that handles the AI logic
from backend.services.ai_resume_service import generate_latex_bullets

app = FastAPI()

# --- 1. Configure CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. Include Routers ---
app.include_router(upload.router)
app.include_router(analysis.router)
app.include_router(resume.router)

# --- 3. AI Refinement Logic ---
class RefineRequest(BaseModel):
    text: str
    role: str

@app.post("/refine-text")
async def refine_text(data: RefineRequest):
    try:
        # 1. Get the raw LaTeX from Gemini service
        refined_latex = generate_latex_bullets(data.text, data.role)
        
        # 2. Create a "Display Version" for the frontend textareas
        # We replace \item with • so the user sees bullets in the browser
        display_text = refined_latex.replace(r"\begin{itemize}", "") \
                                    .replace(r"\end{itemize}", "") \
                                    .replace(r"\item", "•") \
                                    .replace(r"\\", "") \
                                    .strip()
        
        # 3. Return BOTH. The frontend will show 'display', 
        # but you should save 'latex' to send to the PDF generator.
        return {
            "refinedText": display_text, 
            "rawLatex": refined_latex
        }
        
    except Exception as e:
        print(f"Refinement error: {e}")
        return {"error": "Failed to refine text", "refinedText": data.text, "rawLatex": data.text}