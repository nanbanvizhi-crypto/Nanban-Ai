"""
Search your own documents (PDF, Word, text, markdown).

Files in the `documents` folder are split into chunks and saved in data/doc_index.json.
Two search modes, chosen automatically:
  • Embeddings (best): if Ollama + the embedding model are available, chunks become vectors
    and we rank by cosine similarity.
  • Keyword / BM25 (always-free fallback): if embeddings aren't available, we rank chunks by
    a built-in BM25 keyword scorer — pure Python, no model, no setup. So documents ALWAYS work.
Only new or changed files are re-processed.
"""

import json
import math
import re
from pathlib import Path

import numpy as np

import config

INDEX_FILE = config.DATA_DIR / "doc_index.json"
SUPPORTED = {".pdf", ".docx", ".txt", ".md", ".csv"}
CHUNK_SIZE = 900
CHUNK_OVERLAP = 150
EMBED_BATCH = 32


# ---------------------------------------------------------------- reading files

def _read_pages(path: Path) -> list[tuple[int, str]]:
    """Return [(page_number, text), ...]. Non-PDF files count as one page."""
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        from pypdf import PdfReader
        reader = PdfReader(str(path))
        return [(i + 1, page.extract_text() or "") for i, page in enumerate(reader.pages)]
    if suffix == ".docx":
        import docx
        document = docx.Document(str(path))
        return [(1, "\n".join(p.text for p in document.paragraphs))]
    return [(1, path.read_text(encoding="utf-8", errors="ignore"))]


def _chunk(text: str) -> list[str]:
    text = " ".join(text.split())
    if not text:
        return []
    chunks, start = [], 0
    while start < len(text):
        end = start + CHUNK_SIZE
        if end < len(text):
            space = text.rfind(" ", start + CHUNK_SIZE // 2, end)
            end = space if space != -1 else end
        chunks.append(text[start:end].strip())
        if end >= len(text):
            break
        start = max(end - CHUNK_OVERLAP, start + 1)
    return [c for c in chunks if c]


def _embed(texts: list[str]) -> list[list[float]]:
    import ollama
    vectors = []
    for i in range(0, len(texts), EMBED_BATCH):
        response = ollama.embed(model=config.EMBED_MODEL, input=texts[i:i + EMBED_BATCH])
        vectors.extend(response.embeddings)
    return [[round(float(x), 5) for x in v] for v in vectors]


def _embeddings_available() -> bool:
    """True if Ollama is reachable and the embedding model can be used."""
    try:
        import ollama
        ollama.embed(model=config.EMBED_MODEL, input=["ping"])
        return True
    except Exception:
        return False


# ---------------------------------------------------------------- keyword / BM25 fallback

_WORD = re.compile(r"[a-z0-9]+")


def _tok(text: str) -> list[str]:
    return _WORD.findall((text or "").lower())


def _bm25(query: str, entries: list[dict], top_k: int) -> list[dict]:
    """Rank chunks by BM25 (pure Python, no model). entries: [{file,page,text}, ...]."""
    q_terms = set(_tok(query))
    if not q_terms or not entries:
        return []
    docs = [_tok(e["text"]) for e in entries]
    N = len(docs)
    avgdl = sum(len(d) for d in docs) / N if N else 1
    # document frequency per query term
    df = {t: 0 for t in q_terms}
    for d in docs:
        ds = set(d)
        for t in q_terms:
            if t in ds:
                df[t] += 1
    idf = {t: math.log(1 + (N - df[t] + 0.5) / (df[t] + 0.5)) for t in q_terms}
    k1, b = 1.5, 0.75
    scored = []
    for i, d in enumerate(docs):
        dl = len(d) or 1
        score = 0.0
        for t in q_terms:
            if not idf[t]:
                continue
            f = d.count(t)
            if not f:
                continue
            score += idf[t] * (f * (k1 + 1)) / (f + k1 * (1 - b + b * dl / avgdl))
        if score > 0:
            scored.append((score, i))
    scored.sort(reverse=True)
    return [{**entries[i], "score": round(s, 3)} for s, i in scored[:top_k]]


# ---------------------------------------------------------------- index

def _load_index() -> dict:
    try:
        return json.loads(INDEX_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {"embed_model": config.EMBED_MODEL, "files": {}}


def _save_index(index: dict) -> None:
    INDEX_FILE.write_text(json.dumps(index), encoding="utf-8")


def document_files() -> list[Path]:
    return sorted(p for p in config.DOCUMENTS_DIR.iterdir()
                  if p.is_file() and p.suffix.lower() in SUPPORTED)


def refresh_index() -> str:
    """Index new/changed documents and drop deleted ones. Returns a short report.
    Uses embeddings when available, else indexes chunks for keyword search (always works)."""
    index = _load_index()
    if index.get("embed_model") != config.EMBED_MODEL:
        index = {"embed_model": config.EMBED_MODEL, "files": {}}

    use_embed = _embeddings_available()
    files = {p.name: p for p in document_files()}
    removed = [name for name in index["files"] if name not in files]
    for name in removed:
        del index["files"][name]

    added, failed = [], []
    for name, path in files.items():
        mtime = path.stat().st_mtime
        existing = index["files"].get(name, {})
        # re-index if changed, or if embeddings are now available but this file has none
        if existing.get("mtime") == mtime and not (use_embed and not existing.get("vectors")):
            continue
        try:
            chunks = [{"page": page, "text": piece}
                      for page, text in _read_pages(path)
                      for piece in _chunk(text)]
            vectors = []
            if use_embed and chunks:
                try:
                    vectors = _embed([c["text"] for c in chunks])
                except Exception:
                    vectors = []   # fall back to keyword for this file
            index["files"][name] = {"mtime": mtime, "chunks": chunks, "vectors": vectors}
            added.append(name)
        except Exception as e:  # keep going with the other files
            failed.append(f"{name} ({e})")

    _save_index(index)
    mode = "embeddings" if use_embed else "keyword search (no embed model — still works)"
    parts = [f"{len(files)} document(s) ready · mode: {mode}"]
    if added:
        parts.append("indexed: " + ", ".join(added))
    if removed:
        parts.append("removed: " + ", ".join(removed))
    if failed:
        parts.append("failed: " + "; ".join(failed))
    return " | ".join(parts)


def search(query: str, top_k: int = 4) -> list[dict]:
    """Return the most relevant chunks: [{file, page, text, score}, ...].
    Uses embeddings when every chunk has a vector and the model is reachable; else BM25 keyword."""
    index = _load_index()
    all_entries, vec_entries, matrix = [], [], []
    for name, info in index["files"].items():
        vectors = info.get("vectors") or []
        has_vec = len(vectors) == len(info["chunks"]) and len(vectors) > 0
        for i, chunk in enumerate(info["chunks"]):
            e = {"file": name, "page": chunk["page"], "text": chunk["text"]}
            all_entries.append(e)
            if has_vec:
                vec_entries.append(e)
                matrix.append(vectors[i])
    if not all_entries:
        return []

    # try embeddings only if ALL chunks are vectorised and the model answers
    if len(vec_entries) == len(all_entries) and matrix:
        try:
            query_vec = np.array(_embed([query])[0])
            mat = np.array(matrix)
            scores = mat @ query_vec / (np.linalg.norm(mat, axis=1) * np.linalg.norm(query_vec) + 1e-9)
            best = np.argsort(scores)[::-1][:top_k]
            return [{**vec_entries[i], "score": float(scores[i])} for i in best]
        except Exception:
            pass   # model went away → keyword fallback

    return _bm25(query, all_entries, top_k)
