from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Bot settings"""

    bot_token: str = ""
    lms_api_base_url: str = "http://localhost:8000"
    lms_api_key: str = ""
    llm_api_key: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
