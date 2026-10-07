from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = f"sqlite:///{ROOT / 'backend' / 'nilm.db'}"
    jwt_secret: str = "nilm-dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7
    model_dir: str = str(ROOT / "ml" / "checkpoints")
    data_dir: str = str(ROOT / "data")
    cors_origins: str = "*"
    seed_demo: bool = True
    power_limit_w: float = 3000.0


settings = Settings()
