import os
from pathlib import Path

from dotenv import load_dotenv


env_path = Path(__file__).with_name(".env")
load_dotenv(env_path)


class Settings:
    app_name: str = os.getenv("APP_NAME", "Mini Business Inventory Backend")
    environment: str = os.getenv("APP_ENV", "development")
    debug: bool = os.getenv("DEBUG", "true").strip().lower() in {"1", "true", "yes", "on"}


settings = Settings()
