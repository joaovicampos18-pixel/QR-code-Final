"""
db.py - Camada de acesso ao banco de dados (Supabase)
"""
import os
import logging
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

TABLE = "registros_etiquetas"


def conectar() -> Client | None:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        logger.error("SUPABASE_URL ou SUPABASE_KEY não definidos no .env")
        return None
    try:
        return create_client(url, key)
    except Exception as e:
        logger.error(f"Erro ao conectar ao Supabase: {e}")
        return None


def buscar_ultimo_codigo(db: Client) -> int:
    """Retorna o último código gerado, ou 0 se não houver registros."""
    try:
        r = db.table(TABLE).select("fim").order("fim", desc=True).limit(1).execute()
        return int(r.data[0]["fim"]) if r.data else 0
    except Exception as e:
        logger.error(f"Erro ao buscar último código: {e}")
        return 0


def registrar_lote(db: Client, inicio: int, fim: int, quantidade: int) -> bool:
    """Salva no banco o registro do lote gerado. Retorna True se ok."""
    try:
        db.table(TABLE).insert({
            "inicio": inicio,
            "fim": fim,
            "quantidade": quantidade,
        }).execute()
        return True
    except Exception as e:
        logger.error(f"Erro ao registrar lote: {e}")
        return False
