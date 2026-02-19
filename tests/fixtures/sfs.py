import pytest, logging, time
from api.sfs.helper import create_sfs, delete_sfs

logger = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def sfs(api_client, config):
    # Create SFS
    sfs_id = create_sfs(api_client, config, logger)
    yield sfs_id
    # Cleanup SFS
    time.sleep(3)
    delete_sfs(api_client, config, sfs_id, logger)
