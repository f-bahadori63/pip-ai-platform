import os

class Settings:

    APP_NAME = "PIP AI Platform"
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://localhost/pip"
    )

settings = Settings()