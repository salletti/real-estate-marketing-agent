import json
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

_DEFAULT_ALLOWED_HOSTS = [
    "publication-server", "publication-server:8002",
    "localhost", "localhost:8002", "127.0.0.1", "127.0.0.1:8002",
]


class Settings(BaseSettings):
    server_host: str = "0.0.0.0"
    server_port: int = 8002

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
