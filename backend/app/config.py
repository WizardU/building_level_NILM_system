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
    # Comma separated. Docker/dev may use "*" (credentials are then disabled).
    cors_origins: str = (
        "http://localhost:3000,http://127.0.0.1:3000,"
        "http://localhost:3100,http://127.0.0.1:3100"
    )
    seed_demo: bool = True
    power_limit_w: float = 3000.0
    tariff_cny_per_kwh: float = 0.6
    alert_cooldown_minutes: int = 10
    max_page_size: int = 500
    max_range_days: int = 31
    model_preferred: str = "attention"
    display_timezone: str = "Asia/Shanghai"


settings = Settings()
