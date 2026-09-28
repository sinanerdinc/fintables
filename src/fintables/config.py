from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
_ENV_FILE = _PROJECT_DIR / ".env"


class Settings(BaseSettings):
    base_url: str = "https://api.fintables.com"
    gate_url: str = "https://gate.fintables.com"
    mobile_build: int = 323
    mobile_version: str = "2.28.2"
    username: str | None = None
    email: str | None = None
    password: str | None = Field(default=None, repr=False)
    typesense_api_key: str | None = Field(default=None, repr=False)
    lang: str | None = None

    @property
    def email_or_username(self) -> str | None:
        return self.email or self.username

    model_config = SettingsConfigDict(
        env_prefix="FINTABLES_",
        env_file=(_ENV_FILE if _ENV_FILE.is_file() else ".env"),
        extra="ignore",
    )

    @property
    def user_agent(self) -> str:
        return f"fintables-mobile/{self.mobile_build} ({self.mobile_version})"

    @property
    def default_headers(self) -> dict[str, str]:
        return {
            "Host": "api.fintables.com",
            "User-Agent": self.user_agent,
        }

    @property
    def gate_headers(self) -> dict[str, str]:
        headers = {
            "Host": "gate.fintables.com",
            "User-Agent": self.user_agent,
        }
        if self.typesense_api_key:
            headers["x-typesense-api-key"] = self.typesense_api_key
        return headers


settings = Settings()
