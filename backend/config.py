from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Ollama (local) — main agent + detector + sensor manager
    ollama_base_url: str = "http://localhost:11434/v1"
    ollama_model: str = "llama3.1"
    # Native Ollama chat API; leave empty to derive from ollama_base_url
    ollama_chat_url: str = ""
    ollama_timeout_sec: float = 120.0

    # Groq — constitutional judge (optional, only needed when use_judge=True)
    groq_api_key: str = ""
    groq_model: str = "llama3-70b-8192"

    database_url: str = "sqlite:///./iotguard.db"
    frontend_url: str = "http://localhost:3000"

    class Config:
        env_file = ".env"


settings = Settings()
