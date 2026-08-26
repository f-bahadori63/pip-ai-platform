import os

from dotenv import load_dotenv

load_dotenv()


class Settings:

    APP_NAME = "PIP AI Platform"

    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://pip_user:pip_password@localhost:5432/pip_db",
    )

    # Local inference (Ollama)
    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")


settings = Settings()
