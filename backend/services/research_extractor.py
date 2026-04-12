def extract_research(text):

    keywords = [
        "research paper",
        "conference",
        "journal",
        "publication",
        "patent"
    ]

    lines = text.split("\n")
    research = []

    for line in lines:

        line_lower = line.lower()

        if any(keyword in line_lower for keyword in keywords):
            research.append(line.strip())

    return research