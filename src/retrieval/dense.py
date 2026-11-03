
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from pathlib import Path


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
        model=None,
        model_name=MODEL_NAME,
        top_k=DEFAULT_TOP_K
    ):
        if not isinstance(top_k, int) or isinstance(top_k, bool) or top_k <= 0:
            raise ValueError("top_k must be a positive integer.")

        self.collection_name = collection_name
        self.top_k = top_k

        # Reuse an existing model when provided.
        if model is None:
            print("Loading BGE-M3 model...")
            self.model = SentenceTransformer(
                model_name,
                device="cpu"
            )
            self.model.max_seq_length = 512
        else:
            self.model = model

        print("Connecting to Qdrant...")

        self.client = QdrantClient(path=str(QDRANT_DIR))

        if not self.client.collection_exists(collection_name):
            self.client.close()
            raise ValueError(
                f"Collection not found: {collection_name}"
            )

        print(f"Dense Retriever ready: {collection_name}")

    def encode_query(self, query):
        """Convert a query into a normalized embedding."""

        if not isinstance(query, str) or not query.strip():
            raise ValueError("Query must be a non-empty string.")

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

        limit = self.top_k if top_k is None else top_k

        if not isinstance(limit, int) or isinstance(limit, bool) or limit <= 0:
            raise ValueError("top_k must be a positive integer.")

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
                "source_path": payload.get("source_path"),
                "section_type": payload.get("section_type"),
                "section_number": payload.get("section_number"),
                "section_marker": payload.get("section_marker"),
                "chapter_title": payload.get("chapter_title"),
                "paragraph_numbers": payload.get("paragraph_numbers"),
                "passage_index": payload.get("passage_index")
            })

        return results

    def close(self):
        self.client.close()


def main():

    query = "İşverenin risk değerlendirmesi yapma yükümlülüğü nedir?"

    experiments = [
        "isg_size_500_overlap_0",
        "isg_size_1000_overlap_0",
        "isg_size_1000_overlap_100",
        "isg_size_1000_overlap_200",
        "isg_size_1500_overlap_0"
    ]

    # Load BGE-M3 only once.
    print("Loading BGE-M3 model...")
    model = SentenceTransformer(MODEL_NAME, device="cpu")
    model.max_seq_length = 512

    for collection_name in experiments:

        print("\n" + "=" * 60)
        print(f"Collection: {collection_name}")
        print("=" * 60)

        retriever = DenseRetriever(
            collection_name=collection_name,
            model=model
        )

        try:
            results = retriever.search(query, top_k=5)

            for index, result in enumerate(results, start=1):
                print(f"\n{index}. Score: {result['score']:.4f}")
                print(f"Passage ID: {result['passage_id']}")
                print(f"Document: {result['title']}")
                print(f"Section: {result['section_marker']}")
                print(f"Paragraphs: {result['paragraph_numbers']}")
                print(f"Text: {result['text'][:250]}")

        finally:
            retriever.close()


if __name__ == "__main__":
    main()
