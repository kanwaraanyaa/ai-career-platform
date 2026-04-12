# backend/services/report_generator.py
import re 
class ReportGenerator:
    @staticmethod
    def generate_dossier(parsed_resume, gap_data):
        raw_edu = parsed_resume.get("education", "Institutional Background")
        institution = raw_edu.split("from")[-1].split("(")[0].strip() if "from" in raw_edu else raw_edu
        
        # --- 1. PROPER EXPERIENCE HANDLING (Normalized instantly) ---
        raw_experience = parsed_resume.get("experience_details", [])
        experience = [] if raw_experience == "Foundational" else raw_experience
        
        if not experience or len(experience) == 0:
            exp_label = "Project-Based / Academic Focus"
        elif len(experience) == 1:
            exp_label = f"Single Internship ({experience[0].get('company', 'Enterprise')})"
        else:
            exp_label = f"Multi-Firm Portfolio ({len(experience)} Roles)"

        # --- 2. ACADEMIC & RESEARCH LABELS ---
        gpa = parsed_resume.get("gpa", "N/A")
        gpa_label = f"Elite Standing ({gpa} GPA)" if gpa != "N/A" else "Professional Standing"
        
        raw_res = str(parsed_resume.get("research", ""))
        has_research = bool(parsed_resume.get("research") or "Patent" in raw_res or "IEEE" in raw_res)
        research_label = "International Research/Patent Impact" if has_research else "Applied Engineering"

        # --- INITIALIZE LISTS ---
        strengths = []
        missing = gap_data.get("missing_skills", [])
        weaknesses = []
        if missing:
    # Groups the top 3-4 missing skills into one professional sentence
            skill_string = ", ".join(missing[:4])
            weaknesses.append(f"Significant technical alignment gap in: {skill_string}")

        # --- 3. ACADEMIC & RESEARCH STRENGTHS ---
        if gpa != "N/A":
            try:
                if float(gpa) > 8.5:
                    strengths.append(f"Strong Academic Pedigree ({gpa} GPA)")
            except ValueError:
                pass
        
        if has_research:
            strengths.append("Verified Research & Patent Contributor")

        # --- THE CRITICAL FIX: Add Project Density and Experience Gaps ---
        if not experience or len(experience) == 0:
            strengths.append("High Architectural Aptitude through Project Density")
            weaknesses.append("Lack of formal corporate or enterprise internship experience")

        # --- 4. DYNAMIC CODING STATS (BRUTE FORCE) ---
        coding = gap_data.get("coding_stats", {}) or {}
        
        # 1. Standard attempt
        solved_count = coding.get("problems_solved") or coding.get("totalSolved") or coding.get("total_solved") or 0
        
        # 2. THE BULLETPROOF REGEX (Ignores single/double quotes entirely)
        if not solved_count or solved_count == 0:
            coding_str = str(coding).lower()
            # This handles 'solved': 52, "solved": 52, and even solved: 52
            match = re.search(r"['\"]?(?:total_?solved|problems_?solved|count|solved)['\"]?\s*:\s*(\d+)", coding_str)
            solved_count = int(match.group(1)) if match else 0

        # 3. STRENGTH / WEAKNESS LOGIC
        try:
            solved_count = int(solved_count)
            if solved_count >= 100:
                strengths.append(f"High Algorithmic Proficiency ({solved_count} LeetCode Solved)")
            elif solved_count > 0:
                weaknesses.append(f"Limited competitive coding footprint ({solved_count} LeetCode Solved)")
            else:
                weaknesses.append("No verified competitive coding profile (0 LeetCode Solved)")
        except (ValueError, TypeError):
            weaknesses.append("No verified competitive coding profile (0 LeetCode Solved)")

        # --- 5. DYNAMIC GITHUB STATS (Strengths & Weaknesses) ---
        active_days = gap_data.get("github_stats", {}).get("activeDays", 0)
        
        if active_days == 0:
            weaknesses.append("Dormant GitHub activity signal (0 Active Days)")
        elif active_days < 15:
            weaknesses.append(f"Low GitHub activity signal ({active_days} Active Days)")
        else:
            strengths.append(f"Active Contributor Signal ({active_days} Days Active)")

        # --- 6. REFACTORING SUGGESTIONS ---
        suggestions = []
        if missing:
            suggestions.append({
                "type": "Skill Bridge",
                "instruction": f"Prioritize hands-on projects in {missing[0]} to bridge the primary technical gap identified for this role."
            })

        projects = parsed_resume.get("projects", [])
        if projects:
            top_project = projects[0].get("title", "Core Projects")
            suggestions.append({
                "type": "Technical Refactoring",
                "instruction": f"Enhance the description of '{top_project}' by adding specific production metrics to demonstrate high-concurrency impact."
            })

        return {
            "college_tier": institution[:40] + "..." if len(institution) > 40 else institution,
            "company_tier": exp_label,
            "gpa_signal": gpa_label,
            "research_signal": research_label,
            "strengths": strengths, 
            "suggestions": suggestions,
            "weaknesses": weaknesses
        }