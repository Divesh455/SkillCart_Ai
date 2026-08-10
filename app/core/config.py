import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    GEMINI_API_KEY: str = Field(default="")
    GROQ_API_KEY: str = Field(default="")
    LLM_PROVIDER: str = Field(default="gemini")  # "gemini" or "groq"
    GEMINI_MODEL: str = Field(default="gemini-2.5-flash")
    GROQ_MODEL: str = Field(default="llama-3.3-70b-versatile")
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)
    DEBUG: bool = Field(default=False)
    DATABASE_URL: str = Field(default="")
    RESUME_DATABASE_URL: str = Field(default="")
    RAILWAY_API: str
    QDRANT_URL : str
    QDRANT_API_KEY : str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
