import re

def extract_education(text):

    lines = text.split("\n")
    education = []
    capture = False
    count = 0

    for line in lines:

        line_lower = line.lower()

        # detect education section
        if "education" in line_lower or "academic" in line_lower:
            capture = True
            continue

        # stop when new section starts
        if capture and any(section in line_lower for section in [
            "experience",
            "projects",
            "skills",
            "certification",
            "achievements",
            "activities"
        ]):
            break

        if capture:
            clean_line = line.strip()

            if len(clean_line) > 5:
                education.append(clean_line)
                count += 1

        # limit lines to avoid extra text
        if count >= 6:
            break

    return education