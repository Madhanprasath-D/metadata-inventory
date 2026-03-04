from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
  mongo_uri: str = ""
  mongo_db: str = "inventory_db"
  http_timeout: int = 30

  model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

# instance used across the application
settings = Settings()