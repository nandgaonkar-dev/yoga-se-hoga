import json
from functools import lru_cache

import chromadb
from sentence_transformers import SentenceTransformer

from app.config import settings


@lru_cache(maxsize=1)
def _get_model() -> SentenceTransformer:
    return SentenceTransformer(settings.embedding_model)


@lru_cache(maxsize=1)
def _get_collection():
    client = chromadb.PersistentClient(path=str(settings.chroma_dir))
    return client.get_collection(settings.chroma_collection_name)


def retrieve_poses(query: str, k: int = settings.retrieval_top_k) -> list[dict]:
    model = _get_model()
    collection = _get_collection()

    query_embedding = model.encode([query]).tolist()
    results = collection.query(query_embeddings=query_embedding, n_results=k)

    metadatas = results["metadatas"][0]
    return [json.loads(metadata["pose_json"]) for metadata in metadatas]
