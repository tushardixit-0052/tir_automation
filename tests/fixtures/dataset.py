import pytest, logging, time
from api.dataset.helper import create_dataset, delete_dataset, ensure_dataset_ready

logger = logging.getLogger(__name__)


# Disk Dataset creation and deletion fixture
@pytest.fixture(scope="module")
def dataset(api_client, config):

    dataset_info = create_dataset(api_client, config, logger)
    dataset_id = dataset_info["id"]
    ensure_dataset_ready(api_client, config, dataset_id, logger)
    yield dataset_info
    delete_dataset(api_client, config, dataset_id, logger)
