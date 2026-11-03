
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from pathlib import Path


# Project configuration
BASE_DIR = Path(__file__).resolve().parents[2]

QDRANT_DIR = BASE_DIR / "data" / "qdrant"

MODEL_NAME = "BAAI/bge-m3"
COLLECTION_NAME = "isg_size_1000_overlap_0"

VECTOR_SIZE = 1024
DEFAULT_TOP_K = 5


class DenseRetriever:

    def __init__(
        self,
        collection_name=COLLECTION_NAME,
        model_name=MODEL_NAME,
        top_k=DEFAULT_TOP_K
    ):
        self.collection_name = collection_name
        self.top_k = top_k

        print("Loading BGE-M3 model...")

        self.model = SentenceTransformer(
            model_name,
            device="cpu"
        )

        self.model.max_seq_length = 512

        print("Connecting to Qdrant...")

        self.client = QdrantClient(
            path=str(QDRANT_DIR)
        )

        if not self.client.collection_exists(collection_name):
            self.client.close()
            raise ValueError(
                f"Collection not found: {collection_name}"
            )

        print("Dense Retriever is ready.")

    def encode_query(self, query):
        """Convert user query into a normalized embedding."""

        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        embedding = self.model.encode(
            [query],
            normalize_embeddings=True,
            convert_to_numpy=True
        )

        vector = embedding[0].tolist()

        if len(vector) != VECTOR_SIZE:
            raise ValueError(
                f"Expected {VECTOR_SIZE} dimensions, "
                f"got {len(vector)}"
            )

        return vector

    def search(self, query, top_k=None):
        """Retrieve the most relevant passages from Qdrant."""

        limit = top_k if top_k is not None else self.top_k

        query_vector = self.encode_query(query)

        response = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=limit,
            with_payload=True
        )

        results = []

        for point in response.points:
            payload = point.payload or {}

            results.append({
                "passage_id": payload.get("passage_id"),
                "score": float(point.score),
                "text": payload.get("text", ""),
                "document_id": payload.get("document_id"),
                "title": payload.get("title"),
                "category": payload.get("category"),
                "section_type": payload.get("section_type"),
                "section_number": payload.get("section_number"),
                "section_marker": payload.get("section_marker"),
                "chapter_title": payload.get("chapter_title")
            })

        return results

    def close(self):
        self.client.close()


def main():

    query = (
        "İşverenin risk değerlendirmesi "
        "yapma yükümlülüğü nedir?"
    )

    experiments = [
        "isg_size_500_overlap_0",
        "isg_size_1000_overlap_0",
        "isg_size_1000_overlap_100",
        "isg_size_1000_overlap_200",
        "isg_size_1500_overlap_0"
    ]

    for collection_name in experiments:

        print("\n" + "=" * 60)
        print(f"Collection: {collection_name}")
        print("=" * 60)

        retriever = DenseRetriever(
            collection_name=collection_name
        )

        try:
            results = retriever.search(query, top_k=5)

            for index, result in enumerate(results, start=1):
                print(
                    f"\n{index}. "
                    f"Score: {result['score']:.4f}"
                )
                print(f"Passage ID: {result['passage_id']}")
                print(f"Document: {result['title']}")
                print(f"Section: {result['section_marker']}")
                print(f"Text: {result['text'][:250]}")

        finally:
            retriever.close()


if __name__ == "__main__":
    main()