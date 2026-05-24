from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Zhanbu"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    CORS_ORIGINS: list[str] = ["*"]

    DEFAULT_TZ: str = "Asia/Shanghai"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
