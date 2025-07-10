import os
import json
from ner_training_utils import convert_to_spacy_ner_format, append_training_example

def flatten_values(value):
    """Recursively flatten values from lists/dicts to strings."""
    if isinstance(value, str):
        return [value]
    elif isinstance(value, list):
        vals = []
        for v in value:
            vals.extend(flatten_values(v))
        return vals
    elif isinstance(value, dict):
        vals = []
        for v in value.values():
            vals.extend(flatten_values(v))
        return vals
    return []

label_map = {
    'name': 'NAME',
    'email': 'EMAIL',
    'phone': 'PHONE',
    'linkedin': 'LINKEDIN',
    'summary': 'SUMMARY',
    'skills': 'SKILLS',
    'work_experience': 'WORK_EXPERIENCE',
    'education': 'EDUCATION',
    'certifications': 'CERTIFICATIONS',
    'languages': 'LANGUAGES',
    'projects': 'PROJECTS',
    'address': 'ADDRESS',
    'urls': 'URLS',
    'achievements': 'ACHIEVEMENTS',
    'responsibilities': 'RESPONSIBILITIES',
    'extra_curricular': 'EXTRA_CURRICULAR',
}

output_dir = "output_json"
output_jsonl = "ner_training_data.jsonl"

with open(output_jsonl, 'w', encoding='utf-8') as out_f:
    for filename in os.listdir(output_dir):
        if filename.endswith(".json"):
            base = os.path.splitext(filename)[0]
            json_path = os.path.join(output_dir, filename)
            txt_path = os.path.join(output_dir, f"{base}_raw.txt")
            if not os.path.exists(txt_path):
                print(f"Raw text file missing for {filename}, skipping.")
                continue
            with open(json_path, "r", encoding="utf-8") as f:
                extracted_json = json.load(f)
            with open(txt_path, "r", encoding="utf-8") as f:
                resume_text = f.read()
            entities = []
            for key, label in label_map.items():
                value = extracted_json.get(key)
                for v in flatten_values(value):
                    if v and isinstance(v, str):
                        for start, end in __import__('app.ner_training_utils', fromlist=['find_entity_spans']).find_entity_spans(resume_text, v):
                            entities.append((start, end, label))
            if entities:
                out_f.write(json.dumps({"text": resume_text, "entities": entities}, ensure_ascii=False) + '\n')

print(f"NER training data written to {output_jsonl}") 