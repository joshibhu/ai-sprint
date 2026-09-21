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

    # USD per 1,000,000 tokens — verify against
    # https://platform.openai.com/docs/pricing for your model.
    usd_per_1m_input: float = 0.05
    usd_per_1m_output: float = 0.40

    usd_to_inr: float = 100.0

# Runs once at import — Python's singleton bean. Missing key fails at startup.
settings = Settings()
