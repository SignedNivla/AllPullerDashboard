# config.py
# ============================================================
# Central configuration loader
# Semua credentials dan settings dibaca dari .env
# Import modul ini di mana saja untuk akses config
# ============================================================

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env dari direktori yang sama dengan file ini
_env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=_env_path)


def _require(key: str) -> str:
    """Ambil env var, raise error yang jelas jika tidak ada."""
    val = os.getenv(key)
    if not val:
        raise EnvironmentError(
            f"\n[CONFIG ERROR] Environment variable '{key}' tidak ditemukan.\n"
            f"Pastikan file .env ada di folder yang sama dengan main.py\n"
            f"dan berisi: {key}=<nilai>\n"
        )
    return val


def _optional(key: str, default: str = "") -> str:
    return os.getenv(key, default)


# ── EIU ──────────────────────────────────────────────────────
EIU_API_KEY  = _require("EIU_API_KEY")
EIU_EMAIL    = _require("EIU_EMAIL")
EIU_PASSWORD = _require("EIU_PASSWORD")
EIU_BASE_URL = _optional("EIU_BASE_URL", "https://api.eiu.com/v1")

# ── UNCTAD ───────────────────────────────────────────────────
UNCTAD_CLIENT_ID     = _require("UNCTAD_CLIENT_ID")
UNCTAD_CLIENT_SECRET = _require("UNCTAD_CLIENT_SECRET")
UNCTAD_BULK_BASE     = _optional("UNCTAD_BULK_BASE",
                                  "https://unctadstat-api.unctad.org/bulkdownload")