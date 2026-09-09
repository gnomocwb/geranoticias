import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Carrega variáveis do .env do diretório de execução ou raiz do projeto
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
DEFAULT_HOURS = int(os.getenv("BRIEFING_HOURS", "16"))
DEFAULT_LANGUAGE = os.getenv("BRIEFING_LANGUAGE", "pt-BR")
REPORTS_DIR = BASE_DIR / "reports"
FEEDS_FILE = Path(__file__).resolve().parent / "feeds.json"


def get_api_key() -> Optional[str]:
    """Retorna a chave da API do Gemini a partir do ambiente."""
    return os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")


def load_configured_feeds(custom_file: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Carrega os feeds cadastrados do arquivo JSON."""
    path = custom_file or FEEDS_FILE
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [item for item in data if item.get("enabled", True)]


def ensure_reports_dir() -> Path:
    """Garante que a pasta de relatórios exista."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    return REPORTS_DIR
