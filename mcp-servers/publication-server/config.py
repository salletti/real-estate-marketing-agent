from pydantic_settings import BaseSettings

_DEFAULT_ALLOWED_HOSTS = [
    "publication-server", "publication-server:8002",
    "localhost", "localhost:8002", "127.0.0.1", "127.0.0.1:8002",
]


class Settings(BaseSettings):
    server_host: str = "0.0.0.0"
    server_port: int = 8002

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
