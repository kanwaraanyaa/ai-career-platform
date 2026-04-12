def extract_projects(text):

    lines = text.split("\n")
    projects = []
    capture = False

    stop_sections = [
        "experience","education","skills",
        "certification","achievement","research"
    ]

    for line in lines:

        clean = line.strip()
        lower = clean.lower()

        if "project" in lower:
            capture = True
            continue

        if capture and any(sec in lower for sec in stop_sections):
            break

        if capture:

            if len(clean) > 4 and len(clean) < 80:

                if not clean.lower().startswith(
                    ("developed","built","created","designed","implemented")
                ):
                    projects.append(clean)

    return list(dict.fromkeys(projects))[:5]