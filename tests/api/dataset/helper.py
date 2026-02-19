from payloads import dataset_payloads
from api.paths import DATASET_ENDPOINTS
from assertions.common_assert import assert_response_exists, assert_schema
import time, pytest, logging

POLL_INTERVAL = 10
MAX_WAIT_TIME = 300  # seconds

logger = logging.getLogger(__name__)


def create_dataset(api_client, config, logger):
    logger.info("Creating dataset for module")

    payload = dataset_payloads.create_disk_dataset_payload()
    logger.info("Create payload: %s", payload)

    endpoint = DATASET_ENDPOINTS["create_dataset"].format(
        team_id=config.team_id, project_id=config.project_id
    )
    logger.info("Create endpoint: %s", endpoint)

    response = api_client.post(endpoint, data=payload)

    assert_response_exists(response)
    assert_schema(response.json(), "dataset/create_dataset.json")

    dataset_id = response.json()["data"]["id"]
    dataset_name = response.json()["data"]["name"]
    logger.info("Created dataset with ID: %s", dataset_id)

    return {"id": dataset_id, "name": dataset_name}


def delete_dataset(api_client, config, dataset_id, logger):
    logger.info("Deleting dataset %s", dataset_id)

    endpoint = DATASET_ENDPOINTS["dataset_id_path"].format(
        team_id=config.team_id, project_id=config.project_id, dataset_id=dataset_id
    )
    logger.info("Delete endpoint: %s", endpoint)

    response = api_client.delete(endpoint)
    logger.info("Delete response: %s", response)

    assert_response_exists(response)
    assert_schema(response.json(), "dataset/delete_dataset.json")


def ensure_dataset_ready(api_client, config, dataset_id, logger):
    logger.info("Ensuring dataset %s is ready", dataset_id)

    endpoint = DATASET_ENDPOINTS["dataset_id_path"].format(
        team_id=config.team_id, project_id=config.project_id, dataset_id=dataset_id
    )
    logger.info("Status endpoint: %s", endpoint)

    start_time = time.time()
    while time.time() - start_time < MAX_WAIT_TIME:
        response = api_client.get(endpoint)
        assert_response_exists(response)

        status = response.json()["data"]["status"]
        logger.info("Current dataset status: %s", status)

        if status == "OK":
            logger.info("Dataset %s is ready", dataset_id)
            return
        elif status == "FAILED":
            pytest.fail(f"Dataset {dataset_id} creation failed with error status")

        time.sleep(POLL_INTERVAL)

    pytest.fail(
        f"Dataset {dataset_id} did not become ready within {MAX_WAIT_TIME} seconds"
    )
