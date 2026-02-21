from payloads import sfs_payloads
from api.paths import SFS_ENDPOINTS
from assertions.common_assert import assert_response_exists, assert_schema
import time, pytest, logging

POLL_INTERVAL = 10
MAX_WAIT_TIME = 300  # seconds

logger = logging.getLogger(__name__)


def create_sfs(api_client, config, logger):
    logger.info("Creating SFS for module")

    payload = sfs_payloads.create_sfs_payload()
    logger.info("Create payload: %s", payload)

    endpoint = SFS_ENDPOINTS["create_sfs"].format(
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

    endpoint = SFS_ENDPOINTS["sfs_id_path"].format(
        team_id=config.team_id, project_id=config.project_id, sfs_id=sfs_id
    )
    logger.info("Delete endpoint: %s", endpoint)

    response = api_client.delete(endpoint)

    assert_response_exists(response)
    assert_schema(response.json(), "sfs/delete_sfs.json")

    logger.info("Deleted SFS with ID: %s", sfs_id)


def list_sfs(api_client, config, logger):
    logger.info("Listing all SFS")

    endpoint = SFS_ENDPOINTS["list_sfs"].format(
        team_id=config.team_id, project_id=config.project_id
    )
    logger.info("List endpoint: %s", endpoint)

    response = api_client.get(endpoint)

    if response.status_code != 200:
        raise Exception(f"Failed to list SFS. Status: {response.status_code}")

    return response.json()


def list_attached_notebooks(api_client, config, sfs_id, logger):
    logger.info("Listing notebooks attached to SFS ID: %s", sfs_id)

    endpoint = SFS_ENDPOINTS["list_attached_notebooks"].format(
        team_id=config.team_id, project_id=config.project_id, sfs_id=sfs_id
    )
    logger.info("List attached notebooks endpoint: %s", endpoint)

    response = api_client.get(endpoint, params={"page_no": 1, "per_page": 10})

    if response.status_code != 200:
        raise Exception(f"Failed to list attached notebooks for SFS {sfs_id}. Status: {response.status_code}")

    return response.json()
