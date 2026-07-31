import os
from dotenv import load_dotenv

load_dotenv()


class Settings:

    APP_NAME = "PIP AI Platform"

    DATABASE_URL = os.getenv(
        "DATABASE_URL"
    )


settings = Settings()