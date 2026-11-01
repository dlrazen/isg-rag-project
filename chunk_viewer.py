from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import json

BASE_DIR = Path(__file__).resolve().parent
CHUNKS_DIR = BASE_DIR / "data" / "chunks"
HOST = "127.0.0.1"
PORT = 8000

HTML = r"""<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ISG RAG - Chunk Viewer</title>
<style>
    * { box-sizing: border-box; }
    body {
        margin: 0; padding: 24px; background: #f4f6f8; color: #20252b;
        font-family: Arial, sans-serif;
    }
    main { max-width: 1050px; margin: auto; }
    h1 { margin: 0 0 6px; font-size: 25px; }
    .muted { color: #66717d; font-size: 14px; }
    .panel {
        background: white; border: 1px solid #dce1e6; border-radius: 10px;
        padding: 18px; margin-top: 16px;
    }
    label { display: block; font-weight: 600; margin-bottom: 7px; }
    select, button {
        font-size: 14px; padding: 10px 12px; border: 1px solid #cbd2d9;
        border-radius: 7px; background: white;
    }
    select { width: 100%; }
    button { cursor: pointer; }
    button:disabled { opacity: .4; cursor: not-allowed; }
    .controls { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
    .controls select { flex: 1; min-width: 240px; }
    .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }
    .stat { background: #f7f8fa; padding: 12px; border-radius: 7px; }
    .stat strong { display: block; font-size: 19px; margin-top: 5px; }
    .metadata { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
    .meta-item { border-bottom: 1px solid #edf0f2; padding: 7px 0; overflow-wrap: anywhere; }
    .meta-item span { color: #68737e; display: block; font-size: 12px; margin-bottom: 4px; }
    pre {
        white-space: pre-wrap; overflow-wrap: anywhere; background: #fafbfc;
        border: 1px solid #e6eaee; border-radius: 8px; padding: 16px;
        line-height: 1.55; font-family: Consolas, monospace; font-size: 14px;
        min-height: 180px;
    }
    .warning { color: #9b5b00; }
    @media (max-width: 650px) {
        body { padding: 12px; }
        .stats { grid-template-columns: repeat(2, 1fr); }
        .metadata { grid-template-columns: 1fr; }
    }
</style>
</head>
<body>
<main>
    <h1>ISG RAG — Chunk Viewer</h1>
    <div class="muted">Chunk'ları belge bazında inceleme aracı. Veriler yalnızca yerel bilgisayarından okunur.</div>

    <section class="panel">
        <label for="documentSelect">Belge seç</label>
        <select id="documentSelect"><option value="">Belgeler yükleniyor...</option></select>
    </section>

    <section class="panel">
        <div class="stats">
            <div class="stat"><span class="muted">Toplam chunk</span><strong id="total">-</strong></div>
            <div class="stat"><span class="muted">Seçili chunk</span><strong id="position">-</strong></div>
            <div class="stat"><span class="muted">Karakter</span><strong id="chars">-</strong></div>
            <div class="stat"><span class="muted">Bölüm</span><strong id="section">-</strong></div>
        </div>
    </section>

    <section class="panel">
        <div class="controls">
            <button id="prev" disabled>← Önceki</button>
            <select id="chunkSelect" aria-label="Chunk seç"></select>
            <button id="next" disabled>Sonraki →</button>
        </div>
        <p id="status" class="muted"></p>
    </section>

    <section class="panel">
        <h3>Metadata</h3>
        <div id="metadata" class="metadata"></div>
    </section>

    <section class="panel">
        <h3>Chunk metni</h3>
        <pre id="chunkText">Bir belge seçin.</pre>
    </section>
</main>

<script>
const documentSelect = document.getElementById("documentSelect");
const chunkSelect = document.getElementById("chunkSelect");
const prevButton = document.getElementById("prev");
const nextButton = document.getElementById("next");
let chunks = [];

function addMeta(label, value) {
    const item = document.createElement("div");
    item.className = "meta-item";
    const title = document.createElement("span");
    title.textContent = label;
    const content = document.createElement("div");
    content.textContent = value === null || value === undefined || value === "" ? "-" : value;
    item.append(title, content);
    return item;
}

async function loadDocuments() {
    const response = await fetch("/api/documents");
    if (!response.ok) throw new Error("Belge listesi alınamadı.");
    const documents = await response.json();

    documentSelect.innerHTML = "";
    if (!documents.length) {
        documentSelect.add(new Option("Chunk dosyası bulunamadı", ""));
        return;
    }

    documents.forEach(doc => {
        documentSelect.add(new Option(`${doc.title} (${doc.count} chunk)`, doc.file));
    });
    await loadSelectedDocument();
}

async function loadSelectedDocument() {
    const filename = documentSelect.value;
    if (!filename) return;

    document.getElementById("status").textContent = "Chunk'lar yükleniyor...";
    const response = await fetch("/api/chunks?file=" + encodeURIComponent(filename));
    if (!response.ok) {
        document.getElementById("status").textContent = "Chunk dosyası okunamadı.";
        return;
    }

    chunks = await response.json();
    chunkSelect.innerHTML = "";

    chunks.forEach((chunk, index) => {
        const label = `${index + 1}. ${chunk.section_type || "section"} ${chunk.section_number || ""} — ${chunk.character_count || 0} karakter`;
        chunkSelect.add(new Option(label, String(index)));
    });

    document.getElementById("total").textContent = chunks.length;
    if (chunks.length) showChunk(0);
    else {
        document.getElementById("position").textContent = "0";
        document.getElementById("chars").textContent = "0";
        document.getElementById("section").textContent = "-";
        document.getElementById("metadata").replaceChildren();
        document.getElementById("chunkText").textContent = "Bu belgede chunk bulunmuyor.";
        prevButton.disabled = true;
        nextButton.disabled = true;
    }
    document.getElementById("status").textContent = "İncelemek istediğin chunk'ı seçebilir veya önceki/sonraki düğmelerini kullanabilirsin.";
}

function showChunk(index) {
    if (index < 0 || index >= chunks.length) return;
    const chunk = chunks[index];
    chunkSelect.value = String(index);

    document.getElementById("position").textContent = `${index + 1} / ${chunks.length}`;
    document.getElementById("chars").textContent = chunk.character_count ?? (chunk.text || "").length;
    document.getElementById("section").textContent =
        `${chunk.section_type || "-"} ${chunk.section_number || ""}`.trim();

    const metadata = document.getElementById("metadata");
    metadata.replaceChildren();
    [
        ["chunk_id", chunk.chunk_id],
        ["document_id", chunk.document_id],
        ["title", chunk.title],
        ["category", chunk.category],
        ["source_path", chunk.source_path],
        ["section_type", chunk.section_type],
        ["section_number", chunk.section_number],
        ["chunk_index", chunk.chunk_index]
    ].forEach(([key, value]) => metadata.appendChild(addMeta(key, value)));

    document.getElementById("chunkText").textContent = chunk.text || "";
    prevButton.disabled = index === 0;
    nextButton.disabled = index === chunks.length - 1;
}

documentSelect.addEventListener("change", loadSelectedDocument);
chunkSelect.addEventListener("change", () => showChunk(Number(chunkSelect.value)));
prevButton.addEventListener("click", () => showChunk(Number(chunkSelect.value) - 1));
nextButton.addEventListener("click", () => showChunk(Number(chunkSelect.value) + 1));

document.addEventListener("keydown", event => {
    if (event.target.tagName === "SELECT") return;
    if (event.key === "ArrowLeft") prevButton.click();
    if (event.key === "ArrowRight") nextButton.click();
});

loadDocuments().catch(error => {
    document.getElementById("status").textContent = error.message;
});
</script>
</body>
</html>
"""


class ChunkViewerHandler(BaseHTTPRequestHandler):
    def send_json(self, data, status=200):
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/":
            payload = HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        if parsed.path == "/api/documents":
            CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
            documents = []
            for path in sorted(CHUNKS_DIR.glob("*.json")):
                try:
                    with path.open("r", encoding="utf-8") as file:
                        chunks = json.load(file)
                    title = chunks[0].get("title", path.stem) if chunks else path.stem
                    documents.append({
                        "file": path.name,
                        "title": title,
                        "count": len(chunks)
                    })
                except (OSError, json.JSONDecodeError, AttributeError):
                    continue
            self.send_json(documents)
            return

        if parsed.path == "/api/chunks":
            filename = parse_qs(parsed.query).get("file", [""])[0]
            # Only allow JSON files directly inside data/chunks.
            if not filename or Path(filename).name != filename or not filename.lower().endswith(".json"):
                self.send_json({"error": "Invalid filename"}, 400)
                return

            file_path = CHUNKS_DIR / filename
            if not file_path.is_file():
                self.send_json({"error": "File not found"}, 404)
                return

            try:
                with file_path.open("r", encoding="utf-8") as file:
                    self.send_json(json.load(file))
            except json.JSONDecodeError:
                self.send_json({"error": "Invalid JSON file"}, 500)
            return

        self.send_json({"error": "Not found"}, 404)

    def log_message(self, format, *args):
        print("[Chunk Viewer]", format % args)


def main():
    if not CHUNKS_DIR.exists():
        print(f"Chunk klasörü bulunamadı: {CHUNKS_DIR}")
        print("Önce chunking işlemini çalıştır.")
        return

    server = ThreadingHTTPServer((HOST, PORT), ChunkViewerHandler)
    print("=" * 55)
    print("ISG RAG - CHUNK VIEWER")
    print(f"Chunk klasörü: {CHUNKS_DIR}")
    print(f"Tarayıcı adresi: http://{HOST}:{PORT}")
    print("Durdurmak için Ctrl+C")
    print("=" * 55)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nChunk Viewer kapatılıyor...")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
