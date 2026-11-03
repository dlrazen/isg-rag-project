import json
from pathlib import Path
from statistics import mean

CHUNKS_DIR = Path("data/chunks")

required_fields = [
    "passage_id",
    "document_id",
    "section_type",
    "section_marker",
    "chapter_title",
    "chunk_size",
    "overlap",
    "character_count",
    "text"
]

for experiment_dir in sorted(CHUNKS_DIR.iterdir()):

    if not experiment_dir.is_dir():
        continue

    all_passages = []
    missing_fields = 0
    incorrect_lengths = 0
    ids = []

    for file_path in experiment_dir.glob("*.json"):

        with open(file_path, "r", encoding="utf-8") as f:
            passages = json.load(f)

        all_passages.extend(passages)

        for passage in passages:

            ids.append(passage["passage_id"])

            if any(field not in passage for field in required_fields):
                missing_fields += 1

            if passage["character_count"] != len(passage["text"]):
                incorrect_lengths += 1

    lengths = [
        len(p["text"])
        for p in all_passages
    ]

    print(f"\n{'=' * 45}")
    print(experiment_dir.name)
    print("=" * 45)

    print("Documents:", len(list(experiment_dir.glob("*.json"))))
    print("Passages:", len(all_passages))
    print("Average length:", round(mean(lengths), 2))
    print("Minimum length:", min(lengths))
    print("Maximum length:", max(lengths))
    print("Duplicate IDs:", len(ids) - len(set(ids)))
    print("Missing metadata:", missing_fields)
    print("Incorrect character counts:", incorrect_lengths)