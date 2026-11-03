import json
from pathlib import Path
from collections import Counter

from src.chunking.chunker import parse_sections

PROCESSED_DIR = Path("data/processed")

total_documents = 0
type_counts = Counter()

for file_path in PROCESSED_DIR.glob("*.json"):

    with open(file_path, "r", encoding="utf-8") as f:
        document = json.load(f)

    sections = parse_sections(document.get("full_text", ""))

    total_documents += 1

    document_counts = Counter(
        section["section_type"] for section in sections
    )

    type_counts.update(document_counts)

    print(f"\n{document['file_name']}")
    print("Sections:", len(sections))
    print("Types:", dict(document_counts))

    for section in sections:
        if section["section_type"] in (
            "temporary_article",
            "additional_article",
            "annex"
        ):
            print(
                "  ",
                section["section_type"],
                section["section_number"],
                section["section_marker"]
            )

print("\n" + "=" * 50)
print("TOTAL DOCUMENTS:", total_documents)
print("TOTAL SECTION TYPES:", dict(type_counts))