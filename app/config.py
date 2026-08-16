import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

APP_DIR = Path(__file__).parent


@dataclass(frozen=True)
class Settings:
    groq_api_key: str | None = os.getenv("GROQ_API_KEY")
    groq_model: str = "openai/gpt-oss-20b"
    groq_temperature: float = 0.7
    default_max_retries: int = 3

    embedding_model: str = "all-MiniLM-L6-v2"
    retrieval_top_k: int = 5

    chroma_dir: Path = APP_DIR / "chroma_db"
    chroma_collection_name: str = "yoga_poses"

    knowledge_base_path: Path = APP_DIR / "knowledge_base.json"
    db_path: Path = APP_DIR / "yoga.db"


settings = Settings()
