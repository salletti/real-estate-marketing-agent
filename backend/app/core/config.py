from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "real-estate-marketing-agent"
    environment: str = "development"

    groq_api_key: str = ""
    llm_model: str = "llama-3.3-70b-versatile"

    database_url: str = ""

    checkpointer_provider: str = "memory"   # "memory" | "redis"
    redis_url: str = "redis://redis:6379"

    langchain_tracing_v2: bool = False
    langchain_api_key: str | None = None
    langchain_project: str = "real-estate-marketing-agent"

    llm_logging_enabled: bool = True
    llm_logging_include_content: bool = False

    mcp_content_generation_server_url: str = "http://content-generation-server:8001/sse"
    mcp_publication_server_url: str = "http://publication-server:8002/sse"

    model_config = {"env_file": ".env"}


settings = Settings()
