# backend/services/coding_analyzer.py
import requests
import re

def analyze_coding_profile(url: str):
    """
    Takes a LeetCode or Codeforces URL and extracts live solving stats.
    """
    if not url:
        return None
        
    # --- LEETCODE LOGIC ---
    if "leetcode.com" in url:
        # Extract username (handles leetcode.com/username or leetcode.com/u/username)
        match = re.search(r"leetcode\.com/(?:u/)?([^/]+)", url)
        if not match:
            return None
        username = match.group(1).strip()
        
        # LeetCode uses a GraphQL API
        graphql_url = "https://leetcode.com/graphql"
        query = """
        query getUserProfile($username: String!) {
          matchedUser(username: $username) {
            profile { ranking }
            submitStats {
              acSubmissionNum { difficulty count }
            }
          }
        }
        """
        try:
            response = requests.post(graphql_url, json={"query": query, "variables": {"username": username}})
            data = response.json()
            user_data = data.get("data", {}).get("matchedUser")
            
            if not user_data:
                return {"error": "User not found"}
                
            stats = user_data.get("submitStats", {}).get("acSubmissionNum", [])
            total_solved = next((item["count"] for item in stats if item["difficulty"] == "All"), 0)
            ranking = user_data.get("profile", {}).get("ranking", 0)
            
            return {
                "platform": "LeetCode",
                "username": username,
                "metric_1": f"Top Rank: {ranking:,}",
                "metric_2": f"Problems Solved: {total_solved}"
            }
        except Exception as e:
            print(f"LeetCode Error: {e}")
            return None

    # --- CODEFORCES LOGIC ---
    elif "codeforces.com" in url:
        match = re.search(r"codeforces\.com/profile/([^/]+)", url)
        if not match:
            return None
        username = match.group(1).strip()
        
        try:
            response = requests.get(f"https://codeforces.com/api/user.info?handles={username}")
            data = response.json()
            if data.get("status") != "OK":
                return {"error": "User not found"}
                
            user_info = data["result"][0]
            rating = user_info.get("rating", "Unrated")
            rank = user_info.get("rank", "Unranked").title()
            
            return {
                "platform": "Codeforces",
                "username": username,
                "metric_1": f"Rating: {rating}",
                "metric_2": f"Rank: {rank}"
            }
        except Exception as e:
            print(f"Codeforces Error: {e}")
            return None
    # --- CODECHEF LOGIC ---
    elif "codechef.com" in url:
        # CodeChef URLs usually look like codechef.com/users/username
        match = re.search(r"codechef\.com/users/([^/]+)", url)
        if not match:
            return None
        username = match.group(1).strip()
        
        try:
            # Using a popular open-source community API for CodeChef
            response = requests.get(f"https://codechef-api.vercel.app/handle/{username}")
            if response.status_code != 200:
                return {"error": "User not found"}
                
            data = response.json()
            rating = data.get("currentRating", "Unrated")
            stars = data.get("stars", "0★")
            
            return {
                "platform": "CodeChef",
                "username": username,
                "metric_1": f"Rating: {rating}",
                "metric_2": f"Tier: {stars}"
            }
        except Exception as e:
            print(f"CodeChef Error: {e}")
            return None       
    return None