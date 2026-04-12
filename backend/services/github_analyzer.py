import requests
import re

def analyze_github_profile(github_url: str):
    if not github_url or "github.com" not in github_url:
        return None
        
    match = re.search(r"github\.com/([^/]+)", github_url)
    if not match:
        return None
        
    username = match.group(1).strip()
    
    try:
        user_response = requests.get(f"https://api.github.com/users/{username}")
        if user_response.status_code != 200:
            return {"error": f"Could not find GitHub user: {username}"}
            
        user_data = user_response.json()
        
        repos_response = requests.get(f"https://api.github.com/users/{username}/repos?per_page=100&sort=updated")
        repos_data = repos_response.json() if repos_response.status_code == 200 else []
        
        languages = set()
        total_stars = 0
        
        for repo in repos_data:
            if repo.get("language"):
                languages.add(repo.get("language"))
            total_stars += repo.get("stargazers_count", 0)

        # --- NEW: Fetch Recent Active Days ---
        active_days = set()
        events_response = requests.get(f"https://api.github.com/users/{username}/events/public")
        if events_response.status_code == 200:
            for event in events_response.json():
                # Extracts just the date part (YYYY-MM-DD) from "2024-03-23T10:41:24Z"
                date_str = event.get("created_at", "")[:10]
                if date_str:
                    active_days.add(date_str)
        # --------------------------------------
            
        return {
            "username": username,
            "public_repos": user_data.get("public_repos", 0),
            "followers": user_data.get("followers", 0),
            "total_stars": total_stars,
            "verified_languages": list(languages),
            "recent_active_days": len(active_days), # <-- Pass it to the router!
            "message": "GitHub profile analyzed successfully."
        }
        
    except Exception as e:
        print(f"GitHub API Error: {e}")
        return {"error": "Failed to connect to GitHub API."}