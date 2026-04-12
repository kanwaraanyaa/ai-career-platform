import re
from datetime import datetime

def extract_experience(text):

    lines = text.split("\n")
    experience = []
    capture = False

    stop_sections = [
        "education",
        "skills",
        "projects",
        "certification",
        "achievement",
        "research"
    ]

    date_pattern = r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s?'?(\d{2,4})"
    for line in lines:

        clean = re.sub(r"[•♦❖▪■]", "", line).strip()
        lower = clean.lower()

        # Start when EXPERIENCE section appears
        if any(keyword in lower for keyword in ["experience","work experience","professional experience","employment"]):
            capture = True
            continue

        # Stop when next section begins
        if capture and any(sec in lower for sec in stop_sections):
            break
        if capture:

            # detect job titles
            # detect experience using date pattern
            dates = re.findall(date_pattern, clean.replace("–", "-").replace("'", ""))

            if len(dates) >= 2:

    # try to capture previous line as role/company
                prev_line = ""
                idx = lines.index(line)

                if idx > 0:
                    prev_line = lines[idx-1].strip()

                role_company = prev_line if prev_line else clean

                experience.append({
                    "role_company": role_company,
                    "dates": dates
        })
    return experience


def calculate_duration(dates):

    months_map = {
        "Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,
        "Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12
    }

    if len(dates) < 2:
        return "Unknown"

    start_month = months_map[dates[0][0]]
    start_year = int(dates[0][1])

    end_month = months_map[dates[1][0]]
    end_year = int(dates[1][1])

    if start_year < 100:
        start_year += 2000
    if end_year < 100:
        end_year += 2000

    total_months = (end_year - start_year) * 12 + (end_month - start_month)

    years = total_months // 12
    months = total_months % 12

    return f"{years} years {months} months"
def calculate_total_experience_from_ranges(experience_data):

    month_map = {
        "Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,
        "Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12
    }

    ranges = []

    for exp in experience_data:

        dates = exp["dates"]

        if len(dates) < 2:
            continue

        start_month = month_map[dates[0][0]]
        start_year = int(dates[0][1])

        end_month = month_map[dates[1][0]]
        end_year = int(dates[1][1])

        if start_year < 100:
            start_year += 2000
        if end_year < 100:
            end_year += 2000

        start = start_year * 12 + start_month
        end = end_year * 12 + end_month

        ranges.append((start, end))

    ranges.sort()

    merged = []

    for start, end in ranges:
        if not merged or start > merged[-1][1]:
            merged.append([start, end])
        else:
            merged[-1][1] = max(merged[-1][1], end)

    total_months = sum(end - start for start, end in merged)

    years = total_months // 12
    months = total_months % 12

    return f"{years} years {months} months"