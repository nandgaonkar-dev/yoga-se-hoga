import json

import chromadb
from sentence_transformers import SentenceTransformer

from app.config import settings


def pose_to_text(pose: dict) -> str:
    return (
        f"{pose['name']}. Benefits: {pose['benefits']} "
        f"Contraindications: {pose['contraindications']} "
        f"Difficulty: {pose['difficulty']}."
    )


def build_collection():
    poses = json.loads(settings.knowledge_base_path.read_text())

    model = SentenceTransformer(settings.embedding_model)
    texts = [pose_to_text(pose) for pose in poses]
    embeddings = model.encode(texts).tolist()

    client = chromadb.PersistentClient(path=str(settings.chroma_dir))
    existing = {c.name for c in client.list_collections()}
    if settings.chroma_collection_name in existing:
        client.delete_collection(settings.chroma_collection_name)
    collection = client.create_collection(settings.chroma_collection_name)

    collection.add(
        ids=[str(i) for i in range(len(poses))],
        embeddings=embeddings,
        documents=texts,
        metadatas=[{"pose_json": json.dumps(pose)} for pose in poses],
    )

    return collection


if __name__ == "__main__":
    collection = build_collection()
    print(f"Embedded {collection.count()} poses into collection '{settings.chroma_collection_name}' at {settings.chroma_dir}")
