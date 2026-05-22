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

    # Hostnames supplémentaires à autoriser pour l'endpoint SSE (production).
    # Format comma-separated. Ex. Render : EXTRA_ALLOWED_HOSTS=mon-service.onrender.com,mon-service
    extra_allowed_hosts: str = ""

    @property
    def allowed_hosts(self) -> list[str]:
        hosts = list(_DEFAULT_ALLOWED_HOSTS)
        if self.extra_allowed_hosts:
            hosts.extend(h.strip() for h in self.extra_allowed_hosts.split(",") if h.strip())
        return hosts

    model_config = {"env_file": ".env"}


settings = Settings()
