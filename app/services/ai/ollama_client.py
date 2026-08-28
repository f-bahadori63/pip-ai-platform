import os

import requests

from app.core.config import settings

AI_ENABLED = settings.AI_ENABLED

OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://127.0.0.1:11434",
).rstrip("/")

OLLAMA_URL = f"{OLLAMA_BASE_URL}/api/generate"

MODEL_NAME = os.getenv(
    "OLLAMA_MODEL",
    "qwen2.5:1.5b",
)

# MVP Smart Import Agent model.
# qwen2.5:3b was verified to timeout in the local MVP runtime.


def generate(
    prompt: str,
    timeout: int = 300,
    num_predict: int = 100,
    temperature: float = 0.2,
) -> str:

    if not AI_ENABLED:
        raise RuntimeError(
            "AI generation is disabled for this MVP deployment"
        )

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "keep_alive": "10m",
            "options": {
                "num_predict": num_predict,
                "temperature": temperature,
            },
        },
        timeout=timeout,
    )

    response.raise_for_status()

    data = response.json()

    return str(
        data.get("response", "")
    ).strip()

