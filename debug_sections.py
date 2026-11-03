import json
from pathlib import Path

from src.chunking.chunker import SECTION_PATTERN

file_path = Path("data/processed/a0330acd6b52.json")

with open(file_path, "r", encoding="utf-8") as f:
    document = json.load(f)

for line in document["full_text"].splitlines():

    if "geçici madde" in line.lower():

        match = SECTION_PATTERN.match(line.strip())

        print("\nLINE:", repr(line.strip()))

        if match:
            marker = match.group("marker")

            print("MATCH:", repr(marker))
            print("UPPER:", repr(marker.upper()))
            print(
                "STARTS WITH:",
                marker.upper().startswith("GEÇİCİ MADDE")
            )
        else:
            print("NO MATCH")