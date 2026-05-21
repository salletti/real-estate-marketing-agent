from pydantic import Field
from pydantic_settings import BaseSettings


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
    # Valeur par défaut en dev : nom du service + variantes localhost.
    # Surcharge possible via la variable d'env ALLOWED_HOSTS (liste séparée par virgules).
    # Ne jamais utiliser ["*"] en préproduction/production.
    allowed_hosts: list[str] = Field(
        default=["content-generation-server", "content-generation-server:8001",
                 "localhost", "localhost:8001", "127.0.0.1", "127.0.0.1:8001"],
    )

    model_config = {"env_file": ".env"}


settings = Settings()
