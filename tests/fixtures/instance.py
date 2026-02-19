import pytest, logging
from api.instance.helper import create_instance, delete_instance

logger = logging.getLogger(__name__)


# Instance creation and deletion fixture
@pytest.fixture(scope="module")
def instance(api_client, config):

    instance_id = create_instance(api_client, config, logger)
    yield instance_id
    delete_instance(api_client, config, instance_id, logger)
