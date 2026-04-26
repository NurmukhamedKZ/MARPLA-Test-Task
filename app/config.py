from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    temperature: float = 0.7
    request_timeout: int = 30

    model_config = {"env_file": ".env"}


settings = Settings()
