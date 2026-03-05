# Loads environment variables using Pydantic settings

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
  mongo_uri: str = ""
  mongo_db: str = "metadata_inventory"
  http_timeout: int = 30

  model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

# instance used across the application
settings = Settings()