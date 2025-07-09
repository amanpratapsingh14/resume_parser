import json
import re
from typing import List, Dict, Tuple

def find_entity_spans(text: str, value: str) -> List[Tuple[int, int]]:
    """Find all spans of value in text. Returns list of (start, end) tuples."""
    spans = []
    if not value or not isinstance(value, str):
        return spans
    for match in re.finditer(re.escape(value), text):
        spans.append((match.start(), match.end()))
    return spans

def convert_to_spacy_ner_format(resume_text: str, extracted_json: Dict, label_map: Dict[str, str]) -> List[Tuple[str, Dict]]:
    """
    label_map: dict mapping JSON keys to NER labels, e.g. {'name': 'NAME', 'email': 'EMAIL'}
    Returns: list of (text, {'entities': [(start, end, label), ...]})
    """
    entities = []
    for key, label in label_map.items():
        value = extracted_json.get(key)
        if not value or not isinstance(value, str):
            continue
        for start, end in find_entity_spans(resume_text, value):
            entities.append((start, end, label))
    return [(resume_text, {'entities': entities})]

def append_training_example(jsonl_path: str, example: Tuple[str, Dict]):
    """Append a single training example to a JSONL file."""
    with open(jsonl_path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(example, ensure_ascii=False) + '\n')

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Convert LLM output to spaCy NER training format.")
    parser.add_argument('--resume_text', type=str, required=True, help='Path to resume text file')
    parser.add_argument('--extracted_json', type=str, required=True, help='Path to extracted JSON file')
    parser.add_argument('--output', type=str, default='ner_training_data.json', help='Output JSONL file')
    args = parser.parse_args()

    with open(args.resume_text, 'r', encoding='utf-8') as f:
        resume_text = f.read()
    with open(args.extracted_json, 'r', encoding='utf-8') as f:
        extracted_json = json.load(f)

    label_map = {
        'name': 'NAME',
        'email': 'EMAIL',
        'phone': 'PHONE',
        'linkedin': 'LINKEDIN',
        # Add more as needed
    }
    examples = convert_to_spacy_ner_format(resume_text, extracted_json, label_map)
    for ex in examples:
        append_training_example(args.output, ex)
    print(f"Appended {len(examples)} example(s) to {args.output}") 