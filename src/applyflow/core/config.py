from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # App
    app_title: str = "ApplyFlow"
    app_version: str = "0.1.0"
    debug: bool = False

    # Database
    database_url: str = "postgresql+asyncpg://applyflow:password@localhost:5432/applyflow"

    # ChromaDB
    chroma_host: str = "localhost"
    chroma_port: int = 8000

    # Ollama
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:7b"
    ollama_embed_model: str = "nomic-embed-text"

    # CORS — comma-separated origins in env, e.g. "http://localhost:3000,http://localhost:5173"
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173", "http://localhost:8080"]


settings = Settings()
