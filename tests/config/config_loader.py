import os
import yaml
import pytest


class Config:
    def __init__(self):
        env = os.getenv("ENV")  # prod | groot | loki
        if not env:
            raise RuntimeError("ENV not set (prod | groot | loki)")

        config_path = f"tests/config/{env}.yaml"
        if not os.path.exists(config_path):
            raise RuntimeError(f"Config file not found: {config_path}")

        with open(config_path) as f:
            raw = yaml.safe_load(f)

        self.base_url = raw["base_url"]
        self.timeout = raw.get("timeout", 30)

        # Auth
        self.bearer_token = os.getenv("BEARER_TOKEN")
        self.api_key = os.getenv("API_KEY")
        self.project_id = os.getenv("PROJECT_ID")
        self.team_id = os.getenv("TEAM_ID")

        if not self.bearer_token:
            raise RuntimeError("BEARER_TOKEN not set in environment")

        if not self.api_key:
            raise RuntimeError("API_KEY not set in environment")


@pytest.fixture(scope="session")
def env_config():
    return Config()
