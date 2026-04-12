import spacy
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# load NLP model
nlp = spacy.load("en_core_web_sm")

# load embedding model (BERT based)
model = SentenceTransformer("all-MiniLM-L6-v2")


# load skills database
def load_skills():

    with open("datasets/skills.txt", "r", encoding="utf-8") as f:
        skills = f.read().splitlines()

    return [skill.lower() for skill in skills]


SKILLS_DB = load_skills()


# convert skills → embeddings
skill_embeddings = model.encode(SKILLS_DB)

skill_embeddings = np.array(skill_embeddings).astype("float32")


# create FAISS index
dimension = skill_embeddings.shape[1]

index = faiss.IndexFlatL2(dimension)

index.add(skill_embeddings)


def normalize_text(text):

    text = text.lower()

    replacements = {
        "node.js": "nodejs",
        "react.js": "react",
        "chart.js": "chartjs",
        "powerbi": "power bi"
    }

    for k, v in replacements.items():
        text = text.replace(k, v)

    return text


def extract_skills(text):

    text = normalize_text(text)

    # detect skills section first
    lines = text.split("\n")
    skill_text = ""

    capture = False

    for line in lines:

        lower = line.lower()

        if "skills" in lower:
            capture = True
            continue

        if capture and any(k in lower for k in ["education","experience","projects"]):
            break

        if capture:
            skill_text += " " + line

    if skill_text.strip():
        text = skill_text

    doc = nlp(text)

    phrases = [chunk.text for chunk in doc.noun_chunks]
    phrases += [ent.text for ent in doc.ents]
    phrases += [token.text for token in doc if token.is_alpha]

    phrases = list(set(phrases))

    phrase_embeddings = model.encode(phrases)
    phrase_embeddings = np.array(phrase_embeddings).astype("float32")

    distances, indices = index.search(phrase_embeddings, 1)

    detected = []

    for i in range(len(phrases)):
        if distances[i][0] < 0.8:   # stricter threshold
            detected.append(SKILLS_DB[indices[i][0]])

    return list(set(detected))