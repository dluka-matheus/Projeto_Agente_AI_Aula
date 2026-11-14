"""Módulo de persistência SQLite para protocolos acadêmicos simulados."""
import sqlite3
from datetime import datetime
from typing import Optional, Dict, Any
from src.config import settings

def inicializar_banco() -> None:
    """Cria a tabela de protocolos se não existir e insere registros iniciais."""
    settings.DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(settings.DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS protocolos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero TEXT UNIQUE NOT NULL,
                categoria TEXT NOT NULL,
                descricao TEXT NOT NULL,
                status TEXT NOT NULL,
                criado_em TEXT NOT NULL,
                atualizado_em TEXT NOT NULL
            )
        """)
        conn.commit()

        # Insere SOL-1001 se não existir
        cursor.execute("SELECT numero FROM protocolos WHERE numero = 'SOL-1001'")
        if not cursor.fetchone():
            data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                INSERT INTO protocolos (numero, categoria, descricao, status, criado_em, atualizado_em)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                "SOL-1001",
                "documentos",
                "Solicitação de declaração de matrícula e histórico escolar parcial",
                "Em análise pela Secretaria Acadêmica (previsão: 2 dias úteis)",
                data_atual,
                data_atual
            ))
            conn.commit()

def consultar_protocolo_db(numero: str) -> Optional[Dict[str, Any]]:
    """Consulta um protocolo pelo número (ex: SOL-1001)."""
    inicializar_banco()
    numero_limpo = numero.strip().upper()
    with sqlite3.connect(settings.DATABASE_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT numero, categoria, descricao, status, criado_em, atualizado_em
            FROM protocolos WHERE numero = ?
        """, (numero_limpo,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

def registrar_solicitacao_db(descricao: str, categoria: str = "geral") -> Dict[str, Any]:
    """Cria um novo protocolo e persiste no banco SQLite."""
    inicializar_banco()
    data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with sqlite3.connect(settings.DATABASE_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        # Encontra o maior número sequencial
        cursor.execute("SELECT id FROM protocolos ORDER BY id DESC LIMIT 1")
        last_row = cursor.fetchone()
        next_id = (last_row["id"] + 1) if last_row else 1001
        numero_protocolo = f"SOL-{next_id + 1000}"

        status_inicial = "Registrado - Em análise pela coordenação/secretaria"
        cursor.execute("""
            INSERT INTO protocolos (numero, categoria, descricao, status, criado_em, atualizado_em)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (numero_protocolo, categoria, descricao, status_inicial, data_atual, data_atual))
        conn.commit()

        return {
            "numero": numero_protocolo,
            "categoria": categoria,
            "descricao": descricao,
            "status": status_inicial,
            "criado_em": data_atual
        }

# Inicializa o banco automaticamente ao importar
inicializar_banco()
