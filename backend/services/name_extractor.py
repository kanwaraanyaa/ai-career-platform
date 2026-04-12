import re
import spacy

nlp = spacy.load("en_core_web_sm")

def extract_name(text):

    lines = text.split("\n")
    lines = [line.strip() for line in lines if line.strip()]

    # Step 1: Rule based (top of resume)
    for line in lines[:10]:

        if re.search(r'\d', line):
            continue

        words = line.split()

        if 2 <= len(words) <= 3:
            if all(word[0].isupper() for word in words):
                return line

    # Step 2: NLP fallback
    doc = nlp(text[:1000])

    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text

    return "Name Not Found"