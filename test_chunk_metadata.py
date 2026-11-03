import json
from pathlib import Path

from src.chunking.chunker import create_document_chunks

processed_dir = Path("data/processed")
document_path = next(processed_dir.glob("*.json"))

with open(document_path, "r", encoding="utf-8") as f:
    document = json.load(f)

chunks = create_document_chunks(
    document,
    chunk_size=1000,
    overlap=100
)

print("Document:", document["title"])
print("Total chunks:", len(chunks))

for chunk in chunks[:3]:
    print("\n---")
    print("Passage ID:", chunk["passage_id"])
    print("Section type:", chunk["section_type"])
    print("Section marker:", chunk["section_marker"])
    print("Chapter title:", chunk["chapter_title"])
    print("Text:", chunk["text"][:200])