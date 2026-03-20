from dataclasses import dataclass
from dotenv import load_dotenv
import os

load_dotenv()


@dataclass
class Config:
    x_bearer_token: str
    x_api_key: str
    x_api_secret: str
    x_access_token: str
    x_access_token_secret: str
    anthropic_api_key: str


def load_config() -> Config:
    missing = []
    required = [
        "X_BEARER_TOKEN",
        "X_API_KEY",
        "X_API_SECRET",
        "X_ACCESS_TOKEN",
        "X_ACCESS_TOKEN_SECRET",
        "ANTHROPIC_API_KEY",
    ]
    for key in required:
        if not os.getenv(key):
            missing.append(key)

    if missing:
        raise ValueError(
            f"以下の環境変数が設定されていません: {', '.join(missing)}\n"
            ".env ファイルを確認してください（.env.example を参照）。"
        )

    return Config(
        x_bearer_token=os.environ["X_BEARER_TOKEN"],
        x_api_key=os.environ["X_API_KEY"],
        x_api_secret=os.environ["X_API_SECRET"],
        x_access_token=os.environ["X_ACCESS_TOKEN"],
        x_access_token_secret=os.environ["X_ACCESS_TOKEN_SECRET"],
        anthropic_api_key=os.environ["ANTHROPIC_API_KEY"],
    )
