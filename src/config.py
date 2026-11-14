"""Configurações e variáveis de ambiente do projeto."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega .env do diretório raiz
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings:
    # Provedor e Chaves
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini").lower()
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "").strip()
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gemini-3.1-flash-lite")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "models/gemini-embedding-001")

    # Vector Store & RAG
    VECTOR_STORE_DIR: Path = BASE_DIR / os.getenv("VECTOR_STORE_DIR", "dados_vetoriais")
    KNOWLEDGE_BASE_PATH: Path = BASE_DIR / "base_conhecimento_academica.json"
    TOP_K_RETRIEVAL: int = int(os.getenv("TOP_K_RETRIEVAL", "3"))

    # Banco de Dados de Protocolos
    DATABASE_PATH: Path = BASE_DIR / os.getenv("DATABASE_PATH", "protocolos.db")

    # LangGraph
    RECURSION_LIMIT: int = int(os.getenv("RECURSION_LIMIT", "15"))

settings = Settings()
