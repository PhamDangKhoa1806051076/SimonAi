import logging
from pathlib import Path

import chromadb
from chromadb.config import Settings

from simon.config_loader import load_config

LOGGER = logging.getLogger("simon.memory")


class SimonMemory:
    def __init__(self) -> None:
        cfg = load_config().get("memory", {})
        persist_dir = Path(cfg.get("persist_directory", "chroma_db"))
        persist_dir.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.Client(
            Settings(chroma_db_impl="duckdb+parquet", persist_directory=str(persist_dir))
        )
        self.collection = self.client.get_or_create_collection(
            name=cfg.get("collection_name", "simon_memory")
        )

    def add_memory(self, text: str, metadata: dict | None = None) -> None:
        self.collection.add(documents=[text], metadatas=[metadata or {}], ids=[str(hash(text))])

    def query(self, query_text: str, n_results: int = 3) -> list[str]:
        results = self.collection.query(query_texts=[query_text], n_results=n_results)
        return [doc for doc in results.get("documents", [[]])[0]]
