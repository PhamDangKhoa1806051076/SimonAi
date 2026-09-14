"""
Simon Memory – Long-term memory storage using ChromaDB.
Stores conversations and personal info as vector embeddings for semantic search.
"""

import datetime
import hashlib
import logging
import sys
from pathlib import Path
from typing import Optional

LOGGER = logging.getLogger("simon.memory")

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parent.parent.parent

DEFAULT_PERSIST_DIR = str(BASE_DIR / "chroma_db")


class SimonMemory:
    """ChromaDB-based persistent memory for Simon AI."""

    def __init__(self, persist_dir: Optional[str] = None, collection_name: str = "simon_memory") -> None:
        self._available = False
        try:
            import chromadb

            if not persist_dir:
                persist_path = Path(DEFAULT_PERSIST_DIR)
            else:
                p = Path(persist_dir)
                persist_path = p if p.is_absolute() else (BASE_DIR / p)

            persist_path.mkdir(parents=True, exist_ok=True)

            self.client = chromadb.PersistentClient(path=str(persist_path))
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"},
            )
            self._available = True
            LOGGER.info("Memory initialized: %s (%d entries)", persist_path, self.collection.count())
        except Exception as exc:
            LOGGER.warning("ChromaDB not available, memory disabled: %s", exc)

    @property
    def is_available(self) -> bool:
        return self._available

    @property
    def count(self) -> int:
        if not self._available:
            return 0
        try:
            return self.collection.count()
        except Exception:
            return 0

    def _make_id(self, text: str) -> str:
        """Generate a unique ID from text content."""
        return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]

    def add_memory(self, text: str, metadata: Optional[dict] = None) -> str:
        """Store a piece of information in long-term memory."""
        if not self._available:
            return "Memory không khả dụng."
        try:
            meta = metadata or {}
            meta["timestamp"] = datetime.datetime.now().isoformat()
            doc_id = self._make_id(text + meta["timestamp"])

            self.collection.add(
                documents=[text],
                metadatas=[meta],
                ids=[doc_id],
            )
            LOGGER.info("Memory saved: %s...", text[:50])
            return f"Đã lưu vào bộ nhớ: '{text[:80]}...'" if len(text) > 80 else f"Đã lưu vào bộ nhớ: '{text}'"
        except Exception as exc:
            LOGGER.exception("Failed to add memory")
            return f"Lỗi lưu bộ nhớ: {exc}"

    def add_conversation(self, user_msg: str, assistant_msg: str) -> None:
        """Store a conversation exchange in memory."""
        if not self._available:
            return
        try:
            text = f"Người dùng: {user_msg}\nSimon: {assistant_msg}"
            meta = {
                "type": "conversation",
                "timestamp": datetime.datetime.now().isoformat(),
            }
            doc_id = self._make_id(text + meta["timestamp"])
            self.collection.add(
                documents=[text],
                metadatas=[meta],
                ids=[doc_id],
            )
        except Exception as exc:
            LOGGER.debug("Failed to save conversation to memory: %s", exc)

    def search_memory(self, query: str, n_results: int = 5) -> str:
        """Search memory for relevant information. Returns formatted results."""
        if not self._available:
            return "Memory không khả dụng."
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=min(n_results, self.count) if self.count > 0 else 1,
            )
            docs = results.get("documents", [[]])[0]
            metas = results.get("metadatas", [[]])[0]

            if not docs:
                return "Không tìm thấy thông tin liên quan trong bộ nhớ."

            lines = []
            for i, (doc, meta) in enumerate(zip(docs, metas), 1):
                ts = meta.get("timestamp", "?")
                lines.append(f"[{i}] ({ts[:10]}) {doc}")
            return "Kết quả tìm kiếm bộ nhớ:\n" + "\n".join(lines)
        except Exception as exc:
            LOGGER.exception("Memory search failed")
            return f"Lỗi tìm kiếm bộ nhớ: {exc}"

    def query(self, query_text: str, n_results: int = 3) -> list[str]:
        """Raw query – returns list of matching documents."""
        if not self._available:
            return []
        try:
            count = self.count
            if count == 0:
                return []
            results = self.collection.query(
                query_texts=[query_text],
                n_results=min(n_results, count),
            )
            return results.get("documents", [[]])[0]
        except Exception as exc:
            LOGGER.debug("Memory query failed: %s", exc)
            return []

    def get_recent(self, n: int = 5) -> list[str]:
        """Get the N most recent memory entries."""
        if not self._available:
            return []
        try:
            count = self.count
            if count == 0:
                return []
            results = self.collection.get(
                limit=min(n, count),
            )
            return results.get("documents", [])
        except Exception as exc:
            LOGGER.debug("Failed to get recent memories: %s", exc)
            return []

    def clear_all(self) -> str:
        """Clear all memories."""
        if not self._available:
            return "Memory không khả dụng."
        try:
            name = self.collection.name
            self.client.delete_collection(name)
            self.collection = self.client.get_or_create_collection(
                name=name,
                metadata={"hnsw:space": "cosine"},
            )
            return "Đã xóa toàn bộ bộ nhớ."
        except Exception as exc:
            return f"Lỗi xóa bộ nhớ: {exc}"


# ------------------------------------------------------------------
# Global singleton and tool wrappers
# ------------------------------------------------------------------

_memory_instance: Optional[SimonMemory] = None


def get_memory(persist_dir: Optional[str] = None, collection_name: str = "simon_memory") -> SimonMemory:
    """Get or initialize the global SimonMemory instance."""
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = SimonMemory(persist_dir=persist_dir, collection_name=collection_name)
    return _memory_instance


def save_to_memory(text: str) -> str:
    """Lưu thông tin quan trọng vào bộ nhớ dài hạn của Simon."""
    return get_memory().add_memory(text)


def query_memory(query: str) -> str:
    """Tìm kiếm thông tin trong bộ nhớ dài hạn của Simon."""
    return get_memory().search_memory(query)

