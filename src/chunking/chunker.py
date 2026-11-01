import re
import json
import hashlib

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

PROCESSED_DIR = BASE_DIR / "data" / "processed"
CHUNKS_DIR = BASE_DIR / "data" / "chunks"

TARGET_CHUNK_SIZE = 1200
MAX_CHUNK_SIZE = 1600


# MADDE ve EK başlıklarını bulur.
SECTION_PATTERN = re.compile(
    r"(?m)(?=^(?:MADDE\s+\d+\s*[–—-]|EK[- ]?\d+\b|Ek[- ]?\d+\b))",
    re.IGNORECASE
)


def detect_section(text):
    article_match = re.search(
        r"MADDE\s+(\d+)",
        text,
        re.IGNORECASE
    )

    if article_match:
        return "article", article_match.group(1)

    annex_match = re.search(
        r"(?:EK|Ek)[- ]?(\d+)",
        text
    )

    if annex_match:
        return "annex", annex_match.group(1)

    return "intro", None


def split_long_block(text):
    """
    Uzun bir maddeyi mümkün olduğunca paragraf
    sınırlarından küçük parçalara ayırır.
    """

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    chunks = []
    current_chunk = ""

    for line in lines:

        # Tek satır çok uzunsa cümle sınırlarından böl.
        if len(line) > MAX_CHUNK_SIZE:
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = ""

            sentences = re.split(r"(?<=[.!?])\s+", line)

            for sentence in sentences:
                if (
                    current_chunk
                    and len(current_chunk) + len(sentence) > TARGET_CHUNK_SIZE
                ):
                    chunks.append(current_chunk)
                    current_chunk = sentence
                else:
                    current_chunk = (
                        current_chunk + "\n" + sentence
                        if current_chunk
                        else sentence
                    )

            continue

        if (
            current_chunk
            and len(current_chunk) + len(line) + 1 > TARGET_CHUNK_SIZE
        ):
            chunks.append(current_chunk)
            current_chunk = line
        else:
            current_chunk = (
                current_chunk + "\n" + line
                if current_chunk
                else line
            )

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def create_chunks(document):

    text = document.get("full_text", "").strip()

    if not text:
        return []

    sections = SECTION_PATTERN.split(text)

    # İlk MADDE'den önceki başlık ve belge adını kaybetme.
    if len(sections) > 1:
        prefix = sections[0].strip()

        if prefix:
            sections[1] = prefix + "\n" + sections[1]

    chunks = []

    for section_text in sections:

        section_text = section_text.strip()

        if not section_text:
            continue

        section_type, section_number = detect_section(section_text)

        if len(section_text) <= MAX_CHUNK_SIZE:
            text_parts = [section_text]
        else:
            text_parts = split_long_block(section_text)

        for part in text_parts:

            part = part.strip()

            if not part:
                continue

            chunk_index = len(chunks)

            chunk_id = hashlib.sha256(
                f"{document['document_id']}_{chunk_index}".encode("utf-8")
            ).hexdigest()[:16]

            chunks.append({
                "chunk_id": chunk_id,
                "document_id": document["document_id"],
                "title": document["title"],
                "category": document["category"],
                "source_path": document["source_path"],
                "section_type": section_type,
                "section_number": section_number,
                "chunk_index": chunk_index,
                "character_count": len(part),
                "text": part
            })

    return chunks


def process_all_documents():

    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

    processed_files = list(PROCESSED_DIR.glob("*.json"))

    total_documents = 0
    total_chunks = 0

    for file_path in processed_files:

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                document = json.load(file)

            chunks = create_chunks(document)

            output_path = CHUNKS_DIR / file_path.name

            with open(output_path, "w", encoding="utf-8") as file:
                json.dump(
                    chunks,
                    file,
                    ensure_ascii=False,
                    indent=4
                )

            total_documents += 1
            total_chunks += len(chunks)

            print(
                f"{document['title']}: "
                f"{len(chunks)} chunks oluşturuldu."
            )

        except Exception as error:
            print(f"ERROR: {file_path.name}: {error}")

    print("\n========== CHUNKING SUMMARY ==========")
    print(f"Processed documents: {total_documents}")
    print(f"Total chunks: {total_chunks}")


if __name__ == "__main__":
    process_all_documents()