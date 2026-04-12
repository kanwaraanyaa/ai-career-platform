import re

SECTION_HEADERS = {
    "skills": [
        "skills", "technical skills", "core skills", "technologies"
    ],
    "experience": [
        "experience", "work experience", "professional experience",
        "employment","Experience"
    ],
    "education": [
        "education", "academic background", "academic history"
    ],
    "projects": [
        "projects", "academic projects", "personal projects"
    ],
    "research": [
        "research", "publications", "patents"
    ]
}


def normalize_header(line):

    line = line.lower()

    # remove punctuation
    line = re.sub(r"[:|\-–]", "", line)

    return line.strip()


def split_resume_sections(text):

    lines = text.split("\n")

    sections = {
        "skills": [],
        "experience": [],
        "education": [],
        "projects": [],
        "research": []
    }

    current_section = None

    for line in lines:

        clean = line.strip()

        if not clean:
            continue

        normalized = normalize_header(clean)

        # detect section header
        header_found = False

        for section, keywords in SECTION_HEADERS.items():

            for keyword in keywords:

                if normalized == keyword:
                    current_section = section
                    header_found = True
                    break

            if header_found:
                break

        if header_found:
            continue

        # store content under detected section
        if current_section:
            sections[current_section].append(clean)

    # convert lists → text
    for key in sections:
        sections[key] = "\n".join(sections[key])

    return sections