import os

from dotenv import load_dotenv
from sqlalchemy.engine import URL

load_dotenv()


def _env_flag(name: str, default: bool = False) -> bool:
    value = os.getenv(name)

    if value is None:
        return default

    return value.strip().lower() in {"1", "true", "yes", "on"}


def _database_url():
    explicit_url = os.getenv("DATABASE_URL")

    if explicit_url:
        return explicit_url

    connection_name = os.getenv("CLOUD_SQL_CONNECTION_NAME")

    if connection_name:
        return URL.create(
            drivername="postgresql+psycopg2",
            username=os.getenv("DB_USER", "pip_user"),
            password=os.getenv("DB_PASS", ""),
            database=os.getenv("DB_NAME", "pip_db"),
            query={"host": f"/cloudsql/{connection_name}"},
        )

    return "postgresql+psycopg2://pip_user:pip_password@localhost:5432/pip_db"


class Settings:
    APP_NAME = "PIP AI Platform"
    DATABASE_URL = _database_url()
    SQL_ECHO = _env_flag("SQL_ECHO", default=False)
    AI_ENABLED = _env_flag("AI_ENABLED", default=True)

    # Local inference (disabled in the Cloud Run MVP).
    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")


settings = Settings()
