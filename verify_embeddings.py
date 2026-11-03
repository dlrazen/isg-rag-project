import json
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parent

CHUNKS_DIR = ROOT / "data" / "chunks"
EMBEDDINGS_DIR = ROOT / "data" / "embeddings"

experiments = [
    "size_500_overlap_0",
    "size_1000_overlap_0",
    "size_1500_overlap_0",
    "size_1000_overlap_100",
    "size_1000_overlap_200",
]

for experiment in experiments:

    print(f"\n{'=' * 50}")
    print(experiment)
    print("=" * 50)

    source_dir = CHUNKS_DIR / experiment
    embedding_dir = EMBEDDINGS_DIR / experiment

    source_chunks = []
    embedded_chunks = []

    for file in source_dir.glob("*.json"):
        source_chunks.extend(
            json.loads(file.read_text(encoding="utf-8"))
        )

    for file in embedding_dir.glob("*.json"):
        embedded_chunks.extend(
            json.loads(file.read_text(encoding="utf-8"))
        )

    source_ids = [c["passage_id"] for c in source_chunks]
    embedded_ids = [c["passage_id"] for c in embedded_chunks]

    vectors = np.array([
        c["embedding"] for c in embedded_chunks
    ])

    print("Source chunks:", len(source_chunks))
    print("Embeddings:", len(embedded_chunks))
    print("ID eşleşmesi:", set(source_ids) == set(embedded_ids))
    print("Duplicate IDs:", len(embedded_ids) - len(set(embedded_ids)))
    print("Vector shape:", vectors.shape)
    print("Eksik embedding:", sum(
        "embedding" not in c for c in embedded_chunks
    ))
    print("Finite values:", np.isfinite(vectors).all())

    norms = np.linalg.norm(vectors, axis=1)

    print("Normalized vectors:", np.allclose(norms, 1.0, atol=1e-3))

print("\nVerification completed.")