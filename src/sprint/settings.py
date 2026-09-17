from pydantic_settings import BaseSettings, SettingsConfigDict


# Spring Boot @ConfigurationProperties: subclassing BaseSettings does the binding.
class Settings(BaseSettings):
    # Magic name pydantic looks for. "model" = data model, not an LLM.
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # unknown keys in .env are skipped, not an error
    )

    # Field name <- env var, case-insensitive. Pydantic enforces these hints at
    # runtime; plain Python would ignore them. Precedence: env var > .env > default.
    openai_api_key: str                 # no default => required
    openai_model: str = "gpt-5.4-mini"  # override with OPENAI_MODEL


# Runs once at import — Python's singleton bean. Missing key fails at startup.
settings = Settings()
