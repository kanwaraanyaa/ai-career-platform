import os
import subprocess
import jinja2
from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import re

router = APIRouter()

# --- Models remain the same ---
class Experience(BaseModel):
    company: str
    role: str
    location: str
    startDate: str
    endDate: str
    current: bool
    description: str

class Project(BaseModel):
    title: str
    description: str

class Research(BaseModel):
    title: str
    description: str
    date: str

class Certification(BaseModel):
    name: str
    issuer: str
    date: str

class ResumeData(BaseModel):
    template_id: str
    full_name: str
    email: str
    phone: Optional[str] = ""
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = ""          # ADDED
    coding_profile_url: Optional[str] = ""  # ADDED
    job_title: str
    university_name: str
    degree_major: str
    graduation_year: str
    core_skills: str
    experiences: List[Experience] 
    projects: List[Project]
    research: List[Research]
    certifications: List[Certification]

def cleanup_files(file_paths: list):
    for path in file_paths:
        if os.path.exists(path):
            try:
                os.remove(path)
            except Exception as e:
                print(f"Cleanup error: {e}")

@router.post("/generate-pdf")
async def generate_pdf(data: ResumeData, background_tasks: BackgroundTasks):
    template_dir = os.path.abspath('./backend/templates')
    
    # 1. Initialize Jinja2
    latex_jinja_env = jinja2.Environment(
        block_start_string='\BLOCK{',
        block_end_string='}',
        variable_start_string='<<',
        variable_end_string='>>',
        comment_start_string='\#{',
        comment_end_string='}',
        trim_blocks=True,
        autoescape=False,
        loader=jinja2.FileSystemLoader(template_dir)
    )

    # 2. Select Template - CRITICAL: This defines the 'template' variable
    template_name = f"{data.template_id}.tex"
    if not os.path.exists(os.path.join(template_dir, template_name)):
        template_name = 'modern.tex'

    try:
        template = latex_jinja_env.get_template(template_name)
    except Exception as e:
        return {"error": f"Template loading error: {str(e)}"}

    # 3. Pre-process
    def sanitize_for_latex(text: str):
        if not text: return ""
        chars = {"&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_"}
        for char, replacement in chars.items():
            text = re.sub(f"(?<!\\\\){re.escape(char)}", replacement, text)
        return text
    
   # --- CORE SKILLS PROCESSING (Alignment Fix) ---
    raw_skills = data.core_skills.strip()

# 1. Sanitize for symbols (&, %, etc.)
    sanitized_skills = sanitize_for_latex(raw_skills)

# 2. Automatically bold categories AND force a new line (\par) 
# for every category found (text ending in a colon).
    processed_skills = re.sub(
        r"([a-zA-Z\s\\&/]+:)", 
        r"\\par\\noindent\\textbf{\1}", 
        sanitized_skills
    )

# 3. Clean up the very first line so there isn't a blank gap at the top
    processed_skills = re.sub(r"^\\par", "", processed_skills)

    # --- UPDATED EXPERIENCE PROCESSING ---
    processed_experiences = []
    for e in data.experiences:
        exp_dict = e.model_dump()
        
        # SANITIZE Company, Role, and Location (The Missing Step!)
        exp_dict['company'] = sanitize_for_latex(exp_dict['company'])
        exp_dict['role'] = sanitize_for_latex(exp_dict['role'])
        exp_dict['location'] = sanitize_for_latex(exp_dict['location'])
        
        desc = exp_dict['description'].strip()
        if desc and "\\begin{itemize}" not in desc:
            lines = desc.replace("•", "\n").split("\n")
            items = [f"\\item {sanitize_for_latex(l.strip())}" for l in lines if l.strip()]
            exp_dict['description'] = f"\\begin{{itemize}} {' '.join(items)} \\end{{itemize}}" if items else ""
        processed_experiences.append(exp_dict)

    # --- UPDATED PROJECTS PROCESSING ---
    processed_projects = []
    for p in data.projects:
        proj_dict = p.model_dump()
        
        # SANITIZE Title
        proj_dict['title'] = sanitize_for_latex(proj_dict['title'])
        
        desc = proj_dict['description'].strip()
        if desc and "\\begin{itemize}" not in desc:
            lines = desc.replace("•", "\n").split("\n")
            items = [f"\\item {sanitize_for_latex(l.strip())}" for l in lines if l.strip()]
            proj_dict['description'] = f"\\begin{{itemize}} {' '.join(items)} \\end{{itemize}}" if items else ""
        processed_projects.append(proj_dict)

        # --- ADD THIS: RESEARCH PROCESSING ---
    processed_research = []
    for r in data.research:
        res_dict = r.model_dump()
        res_dict['title'] = sanitize_for_latex(res_dict['title'])
        res_dict['date'] = sanitize_for_latex(res_dict['date'])
        
        desc = res_dict['description'].strip()
        # Convert bullets to LaTeX itemize, just like Experience
        if desc and "\\begin{itemize}" not in desc:
            lines = desc.replace("•", "\n").split("\n")
            items = [f"\\item {sanitize_for_latex(l.strip())}" for l in lines if l.strip()]
            res_dict['description'] = f"\\begin{{itemize}} {' '.join(items)} \\end{{itemize}}" if items else ""
        else:
            res_dict['description'] = sanitize_for_latex(desc)
            
        processed_research.append(res_dict)

    # 4. Render
    try:
        merged_tex = template.render(
            full_name=sanitize_for_latex(data.full_name),
            email=sanitize_for_latex(data.email),
            phone=sanitize_for_latex(data.phone),
            # URLs handle stripping prefixes
            linkedin_url=(data.linkedin_url or "").replace("https://", "").replace("http://", ""), 
            github_url=(data.github_url or "").replace("https://", "").replace("http://", ""),
            coding_profile_url=(data.coding_profile_url or "").replace("https://", "").replace("http://", ""),
            
            university_name=sanitize_for_latex(data.university_name),
            degree_major=sanitize_for_latex(data.degree_major),
            graduation_year=data.graduation_year,
            core_skills=processed_skills,  # Use the processed_skills variable here!
            job_title=sanitize_for_latex(data.job_title),
            
            experiences=processed_experiences,
            projects=processed_projects,
            
            research=processed_research,
            
            # Sanitizing all Certification fields
            certifications=[{
                "name": sanitize_for_latex(c.name),
                "issuer": sanitize_for_latex(c.issuer),
                "date": sanitize_for_latex(c.date)
            } for c in data.certifications]
        )
    except Exception as e:
        return {"error": f"Template rendering error: {str(e)}"}

    # 5. File Operations
    # Remove dots and spaces from filename to avoid MiKTeX issues
    clean_name = re.sub(r'[^a-zA-Z0-9]', '_', data.full_name)
    tex_filepath = f"temp_{clean_name}.tex"
    pdf_filepath = f"temp_{clean_name}.pdf"

    with open(tex_filepath, "w", encoding="utf-8") as f:
        f.write(merged_tex)

    # 6. Compile with Increased Timeout
    try:
        # MiKTeX on Windows needs more time (60s)
        subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", tex_filepath],
            check=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            timeout=60 
        )
    except subprocess.TimeoutExpired:
        return {"error": "LaTeX compilation timed out. MiKTeX might be downloading packages."}
    except subprocess.CalledProcessError as e:
        error_log = e.stdout.decode('utf-8', errors='ignore')
        print(error_log)
        return {"error": "LaTeX Compilation Error. Check your dummy data for special characters."}

    # 7. Cleanup
    files_to_delete = [
        tex_filepath, 
        f"temp_{clean_name}.aux", 
        f"temp_{clean_name}.log", 
        f"temp_{clean_name}.out", 
        pdf_filepath
    ]
    background_tasks.add_task(cleanup_files, files_to_delete)

    return FileResponse(
        path=pdf_filepath, 
        media_type="application/pdf", 
        filename=f"{clean_name}_Resume.pdf"
    )