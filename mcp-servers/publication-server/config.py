from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    server_host: str = "0.0.0.0"
    server_port: int = 8002

    # En-têtes Host autorisés pour l'endpoint SSE.
    # Valeur par défaut en dev : nom du service + variantes localhost.
    # Surcharge possible via la variable d'env ALLOWED_HOSTS (liste séparée par virgules).
    # Ne jamais utiliser ["*"] en préproduction/production.
    allowed_hosts: list[str] = Field(
        default=["publication-server", "publication-server:8002",
                 "localhost", "localhost:8002", "127.0.0.1", "127.0.0.1:8002"],
    )

    model_config = {"env_file": ".env"}


settings = Settings()
