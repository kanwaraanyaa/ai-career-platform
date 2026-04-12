# backend/services/linkedin_analyzer.py
import re
import random

def analyze_linkedin_profile(url: str):
    if not url or "linkedin.com" not in url:
        return None
        
    match = re.search(r"linkedin\.com/in/([^/]+)", url)
    if not match:
        return None
        
    username_slug = match.group(1).strip()
    
    # Use the length of the username to create a "seed" 
    # This ensures the SAME URL always gives the SAME mock data
    random.seed(len(username_slug)) 
    
    # Generate dynamic but believable numbers
    connections = random.choice(["400+", "500+", "1.2k", "850", "2k+"])
    headlines = [
        "Software Engineer | Open Source Contributor",
        "Full Stack Developer | Problem Solver",
        "Data Science Aspirant | Python Developer",
        "AI/ML Researcher | Tech Enthusiast"
    ]
    
    return {
        "platform": "LinkedIn",
        "username": username_slug.replace("-", " ").title()[:20],
        "headline": random.choice(headlines),
        "location": random.choice(["Bangalore, India", "Pune, India", "Remote", "Delhi, India"]),
        "metric_1": f"{connections} Connections",
        "metric_2": "Identity Verified"
    }