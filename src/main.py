
import json
import hashlib

from pathlib import Path
from datetime import datetime, timezone

from src.ingestion.loader import load_documents
from src.ingestion.extractor import extract_document
from src.ingestion.cleaner import clean_pages


BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"


def get_document_category(file_path):
    """Get category from the parent folder."""

    relative_path = file_path.relative_to(RAW_DIR)

    if len(relative_path.parts) > 1:
        return relative_path.parts[0]

    return "uncategorized"


def get_document_id(file_path):
    """Generate stable ID based on file path."""

    relative_path = file_path.relative_to(RAW_DIR)

    return hashlib.sha256(
        str(relative_path).encode("utf-8")
    ).hexdigest()[:12]


def process_document(file_path):
    """Extract, clean and prepare a document."""

    print(f"\nProcessing: {file_path.name}")

    pages = extract_document(file_path)
    pages = clean_pages(pages)

    full_text = "\n\n".join(
        page["text"] for page in pages
    )

    # Detect potentially scanned PDFs
    empty_pages = [
        page["page_number"]
        for page in pages
        if not page["text"].strip()
    ]

    document = {
        "document_id": get_document_id(file_path),
        "title": file_path.stem,
        "file_name": file_path.name,
        "file_type": file_path.suffix.lower(),
        "category": get_document_category(file_path),
        "source_path": str(
            file_path.relative_to(RAW_DIR)
        ),
        "file_modified_at": datetime.fromtimestamp(
            file_path.stat().st_mtime,
            tz=timezone.utc
        ).isoformat(),
        "processed_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "language": "tr",
        "page_count": len(pages),
        "character_count": len(full_text),
        "empty_pages": empty_pages,
        "needs_ocr": bool(empty_pages),
        "pages": pages,
        "full_text": full_text
    }

    return document


def save_document(document):
    """Save extracted document as JSON."""

    PROCESSED_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path = (
        PROCESSED_DIR /
        f"{document['document_id']}.json"
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            document,
            file,
            ensure_ascii=False,
            indent=4
        )

    return output_path


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--experiment",
        type=str,
        help="İşlenecek deneyin adı. Belirtilmezse tüm deneyler işlenir."
    )

    args = parser.parse_args()

    if args.experiment:
        experiments = [args.experiment]
    else:
        experiments = sorted(
            d.name for d in CHUNKS_DIR.iterdir()
            if d.is_dir()
            and not (OUTPUT_DIR / d.name).exists()
        )

    print("BGE-M3 modeli yükleniyor...")

    model = SentenceTransformer(
        MODEL_NAME,
        device="cpu"
    )

    model.max_seq_length = 512

    print("Model hazır.")

    for experiment in experiments:
        process_experiment(model, experiment)

    print("\nTüm embedding işlemleri tamamlandı!")


if __name__ == "__main__":
    main()

