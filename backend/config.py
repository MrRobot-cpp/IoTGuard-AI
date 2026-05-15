from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Ollama (local) — main agent + detector
    ollama_base_url: str = "http://localhost:11434/v1"
    ollama_model: str = "llama3.2"

    # Groq — constitutional judge (optional, only needed when use_judge=True)
    groq_api_key: str = ""
    groq_model: str = "llama3-70b-8192"

    database_url: str = "sqlite:///./iotguard.db"
    frontend_url: str = "http://localhost:3000"

    class Config:
        env_file = ".env"


settings = Settings()
