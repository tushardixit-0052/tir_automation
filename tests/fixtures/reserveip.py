import pytest, logging, time
from api.reserveip.helper import reserve_new_ip, delete_reserved_ip

logger = logging.getLogger(__name__)

@pytest.fixture(scope="module")
def reserved_ip(api_client, config):
    # Reserve a new IP
    reserved_ip_id = reserve_new_ip(api_client, config)
    yield reserved_ip_id
    # Cleanup Reserved IP
    time.sleep(3)
    delete_reserved_ip(api_client, config, reserved_ip_id)