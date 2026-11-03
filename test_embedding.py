from sentence_transformers import SentenceTransformer
import numpy as np

# Modeli CPU üzerinde yükle
print("BGE-M3 modeli yükleniyor...")

model = SentenceTransformer(
    "BAAI/bge-m3",
    device="cpu"
)

print("Model başarıyla yüklendi!")

# Örnek Türkçe metinler
texts = [
    "İşveren, çalışanların iş sağlığı ve güvenliğini sağlamakla yükümlüdür.",
    "İş sağlığı ve güvenliği konusunda çalışanlara eğitim verilmelidir."
]

# Embedding üret
embeddings = model.encode(
    texts,
    normalize_embeddings=True,
    show_progress_bar=True
)

# Sonuçları incele
print("\n--- Embedding Test Sonuçları ---")
print("Embedding shape:", embeddings.shape)
print("Vektör boyutu:", embeddings.shape[1])
print("İlk metnin ilk 10 değeri:", embeddings[0][:10])

# İki metin arasındaki cosine similarity
similarity = np.dot(embeddings[0], embeddings[1])

print("Cosine similarity:", similarity)