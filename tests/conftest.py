import pytest
from clients.base_api_client import BaseApiClient
from config.config_loader import Config
import pytest, logging, time
from fixtures.instance import instance
from fixtures.dataset import dataset
from fixtures.sfs import sfs
# from fixtures.pfs import pfs
from fixtures.reserveip import reserved_ip

logger = logging.getLogger(__name__)


def pytest_sessionstart():
    import os
    from pathlib import Path
    from dotenv import load_dotenv

    env = os.getenv("ENV")
    if not env:
        raise RuntimeError("ENV not set. Use ENV=prod|groot|loki")

    env_file = Path(f"env/{env}.env")
    if env_file.exists():
        load_dotenv(env_file)
    # else: env vars expected to be pre-set (Docker -e flags, CI variables, etc.)


@pytest.fixture(scope="session")
def config():
    return Config()


@pytest.fixture(scope="session")
def api_client(config):
    return BaseApiClient(
        base_url=config.base_url,
        bearer_token=config.bearer_token,
        api_key=config.api_key,
        timeout=config.timeout,
    )
