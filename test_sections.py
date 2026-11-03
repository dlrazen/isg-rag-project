import json
from pathlib import Path

from src.chunking.chunker import parse_sections

processed_dir = Path("data/processed")

target_document = None

for file_path in processed_dir.glob("*.json"):
    with open(file_path, "r", encoding="utf-8") as f:
        document = json.load(f)

    if "7.5.18540" in document.get("file_name", ""):
        target_document = document
        print("Found:", file_path.name)
        break

if target_document is None:
    raise FileNotFoundError("Belge bulunamadı.")

sections = parse_sections(target_document["full_text"])

for section in sections:
    print("\n" + "=" * 60)
    print("Type:", section["section_type"])
    print("Number:", section["section_number"])
    print("Marker:", section["section_marker"])
    print("Chapter:", section["chapter_title"])
    print("Text:", section["text"][:300])