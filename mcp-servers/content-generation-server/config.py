import json
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

_DEFAULT_ALLOWED_HOSTS = [
    "content-generation-server", "content-generation-server:8001",
    "localhost", "localhost:8001", "127.0.0.1", "127.0.0.1:8001",
]


class Settings(BaseSettings):
    groq_api_key: str = ""
    llm_model: str = "llama-3.3-70b-versatile"

    langchain_tracing_v2: bool = False
    langchain_api_key: str | None = None
    langchain_project: str = "real-estate-marketing-agent"

    llm_logging_enabled: bool = True
    llm_logging_include_content: bool = False

    server_host: str = "0.0.0.0"
    server_port: int = 8001

    # En-têtes Host autorisés pour l'endpoint SSE.
    # Surcharge via ALLOWED_HOSTS : JSON array ou liste séparée par virgules.
    # Ex. Render : ALLOWED_HOSTS=mon-service.onrender.com,mon-service
    allowed_hosts: list[str] = Field(default=_DEFAULT_ALLOWED_HOSTS)

    @field_validator("allowed_hosts", mode="before")
    @classmethod
    def parse_allowed_hosts(cls, v: Any) -> Any:
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return _DEFAULT_ALLOWED_HOSTS
            if v.startswith("["):
                return json.loads(v)
            return [h.strip() for h in v.split(",") if h.strip()]
        return v

    model_config = {"env_file": ".env"}


settings = Settings()
