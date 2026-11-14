"""Módulo de RAG e Vector Store com ChromaDB."""
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from langchain_core.documents import Document
from langchain_chroma import Chroma
from src.config import settings

logger = logging.getLogger(__name__)

def obter_funcao_embedding():
    """Retorna a função de embedding do Gemini ou fallback do ChromaDB."""
    if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "sua_chave_gemini_aqui":
        try:
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
            return GoogleGenerativeAIEmbeddings(
                model=settings.EMBEDDING_MODEL,
                google_api_key=settings.GEMINI_API_KEY
            )
        except Exception as e:
            logger.warning(f"Erro ao inicializar GoogleGenerativeAIEmbeddings: {e}. Usando fallback local.")
    
    # Fallback local nativo do Chroma (não consome cota nem precisa de internet)
    from chromadb.utils import embedding_functions
    ef = embedding_functions.DefaultEmbeddingFunction()
    
    # Adaptador para interface LangChain Embeddings
    class ChromaDefaultEmbeddingsAdapter:
        def embed_documents(self, texts: List[str]) -> List[List[float]]:
            return ef(texts)
        def embed_query(self, text: str) -> List[float]:
            return ef([text])[0]
            
    return ChromaDefaultEmbeddingsAdapter()

class RAGManager:
    def __init__(self):
        self.vector_store_dir = settings.VECTOR_STORE_DIR
        self.vector_store: Optional[Chroma] = None
        self.embeddings = obter_funcao_embedding()

    def carregar_documentos(self) -> List[Document]:
        """Lê todos os documentos da base_conhecimento_academica.json."""
        if not settings.KNOWLEDGE_BASE_PATH.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {settings.KNOWLEDGE_BASE_PATH}")

        with open(settings.KNOWLEDGE_BASE_PATH, "r", encoding="utf-8") as f:
            dados = json.load(f)

        documentos = []
        for item in dados:
            # Metadados exigidos pelo edital: ID da fonte e categoria
            metadados = {
                "id": item.get("id"),
                "fonte": item.get("fonte", item.get("id")),
                "categoria": item.get("categoria", "geral"),
                "titulo": item.get("titulo", ""),
                "instituicao": item.get("instituicao", "Instituto Horizonte")
            }
            texto = f"Título: {item.get('titulo')}\nCategoria: {item.get('categoria')}\nConteúdo: {item.get('conteudo')}"
            documentos.append(Document(page_content=texto, metadata=metadados))
        return documentos

    def indexar_base(self, force_reindex: bool = False) -> None:
        """Indexa os documentos no ChromaDB persistente."""
        self.vector_store_dir.mkdir(parents=True, exist_ok=True)
        colecao_nome = "normas_academicas"
        
        # Se force_reindex ou diretório vazio
        self.vector_store = Chroma(
            collection_name=colecao_nome,
            embedding_function=self.embeddings,
            persist_directory=str(self.vector_store_dir)
        )

        # Checa se já tem documentos
        try:
            total = self.vector_store._collection.count()
        except Exception:
            total = 0

        if total == 0 or force_reindex:
            docs = self.carregar_documentos()
            self.vector_store.add_documents(docs)
            logger.info(f"Indexados {len(docs)} documentos no ChromaDB.")

    def buscar(self, query: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """Busca documentos relevantes por similaridade com Top-K configurável."""
        if self.vector_store is None:
            self.indexar_base()

        k = top_k or settings.TOP_K_RETRIEVAL
        docs = self.vector_store.similarity_search(query, k=k)
        
        resultados = []
        for doc in docs:
            resultados.append({
                "conteudo": doc.page_content,
                "fonte": doc.metadata.get("fonte", doc.metadata.get("id")),
                "categoria": doc.metadata.get("categoria"),
                "titulo": doc.metadata.get("titulo")
            })
        return resultados

rag_manager = RAGManager()
