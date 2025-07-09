import os
import json
from ner_training_utils import convert_to_spacy_ner_format, append_training_example

label_map = {
    'name': 'NAME',
    'email': 'EMAIL',
    'phone': 'PHONE',
    'linkedin': 'LINKEDIN',
    # Add more as needed
}

output_dir = "output_json"
output_jsonl = "ner_training_data.json"

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
        examples = convert_to_spacy_ner_format(resume_text, extracted_json, label_map)
        for ex in examples:
            append_training_example(output_jsonl, ex)

print(f"NER training data written to {output_jsonl}") 