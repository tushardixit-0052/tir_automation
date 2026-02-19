from payloads import sfs_payloads
from api.paths import SFS_ENDPIONTS
from assertions.common_assert import assert_response_exists, assert_schema
import time, pytest, logging

POLL_INTERVAL = 10
MAX_WAIT_TIME = 300  # seconds

logger = logging.getLogger(__name__)


def create_sfs(api_client, config, logger):
    logger.info("Creating SFS for module")

    payload = sfs_payloads.create_sfs_payload()
    logger.info("Create payload: %s", payload)

    endpoint = SFS_ENDPIONTS["create_sfs"].format(
        team_id=config.team_id, project_id=config.project_id
    )
    logger.info("Create endpoint: %s", endpoint)

    response = api_client.post(endpoint, data=payload)

    assert_response_exists(response)
    assert_schema(response.json(), "sfs/create_sfs.json")

    sfs_id = response.json()["data"]["id"]
    logger.info("Created SFS with ID: %s", sfs_id)

    return sfs_id


def delete_sfs(api_client, config, sfs_id, logger):
    logger.info("Deleting SFS with ID: %s", sfs_id)

    endpoint = SFS_ENDPIONTS["sfs_id_path"].format(
        team_id=config.team_id, project_id=config.project_id, sfs_id=sfs_id
    )
    logger.info("Delete endpoint: %s", endpoint)

    response = api_client.delete(endpoint)

    assert_response_exists(response)
    assert_schema(response.json(), "sfs/delete_sfs.json")

    logger.info("Deleted SFS with ID: %s", sfs_id)
