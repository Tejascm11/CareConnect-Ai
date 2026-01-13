def match_symptom(text, symptom_aliases, medical_db):
    text = text.lower()
    for key, aliases in symptom_aliases.items():
        for word in aliases:
            if word in text and key in medical_db:
                return key, medical_db[key]
    return None, None