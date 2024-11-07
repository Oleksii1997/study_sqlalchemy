from pydantic_settings import BaseSettings, SettingsConfigDict
import os.path

class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    @property
    def database_url_asyncpg(self):
        """
        postgresql+asyncpg://postgres:postgres@localhost:5432/study_alchemy
        """
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def database_url_psycopg(self):
        """
        postgresql+psycopg://postgres:postgres@localhost:5432/study_alchemy
        """
        return f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    if os.path.exists(".env"):
        model_config = SettingsConfigDict(env_file=".env")
    else:
        model_config = SettingsConfigDict(env_file="../.env")


settings = Settings()
