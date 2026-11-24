from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    database_url: str = 'postgresql+psycopg://meridian:meridian@db:5432/meridian'
    app_demo_mode: bool = False
    crawl_enabled: bool = False


settings = Settings()
