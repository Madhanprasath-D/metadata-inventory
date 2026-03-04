from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
  mongo_uri: str = ""
  mongo_db: str = "inventory_db"
  http_timeout: int = 30


settings = Settings()