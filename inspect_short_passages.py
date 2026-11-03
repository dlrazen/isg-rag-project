import json
from pathlib import Path

CHUNKS_DIR = Path("data/chunks/size_1000_overlap_100")

short_passages = []

for file_path in CHUNKS_DIR.glob("*.json"):
    with open(file_path, "r", encoding="utf-8") as f:
        passages = json.load(f)

    for passage in passages:
        if passage["character_count"] < 200:
            short_passages.append(passage)

print("Short passages:", len(short_passages))

for passage in sorted(
    short_passages,
    key=lambda x: x["character_count"]
)[:20]:

    print("\n" + "=" * 60)
    print("Length:", passage["character_count"])
    print("Document:", passage["title"])
    print("Section:", passage["section_number"])
    print("Text:", repr(passage["text"]))
    import json
from pathlib import Path

CHUNKS_DIR = Path("data/chunks/size_1000_overlap_100")

for file_path in CHUNKS_DIR.glob("*.json"):
    with open(file_path, "r", encoding="utf-8") as f:
        passages = json.load(f)

    for i, passage in enumerate(passages):
        if passage["character_count"] == 9:
            print("\nDOCUMENT:", passage["title"])

            for j in range(max(0, i - 2), min(len(passages), i + 3)):
                p = passages[j]

                print("\n--- Passage", j, "---")
                print("Length:", p["character_count"])
                print("Section:", p["section_number"])
                print(p["text"])