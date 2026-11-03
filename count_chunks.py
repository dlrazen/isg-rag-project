import json
from pathlib import Path

chunks_dir = Path("data/chunks")

for experiment_dir in sorted(chunks_dir.iterdir()):

    if not experiment_dir.is_dir():
        continue

    total = 0

    for file_path in experiment_dir.glob("*.json"):
        with open(file_path, "r", encoding="utf-8") as f:
            passages = json.load(f)

        total += len(passages)

    print(f"{experiment_dir.name}: {total} pasaj")