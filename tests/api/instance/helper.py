from payloads import instance_payloads
from api.paths import INSTANCE_ENDPOINTS
from assertions.common_assert import assert_response_exists, assert_schema
import time, pytest, logging

POLL_INTERVAL = 10
MAX_WAIT_TIME = 300  # seconds

logger = logging.getLogger(__name__)


def create_instance(api_client, config, logger):
    logger.info("Creating node for module")

    endpoint = INSTANCE_ENDPOINTS["create_instance"].format(
        team_id=config.team_id, project_id=config.project_id
    )
    logger.info("Create endpoint: %s", endpoint)

    payload = instance_payloads.create_instance_payload()
    logger.info("Create payload: %s", payload)

    response = api_client.post(endpoint, data=payload)
    assert_response_exists(response)
    assert_schema(response.json(), "instance/create_instance.json")

    instance_id = response.json()["data"]["id"]
    logger.info("Created node with ID: %s", instance_id)

    return instance_id


def delete_instance(api_client, config, instance_id, logger):
    logger.info("Deleting node %s", instance_id)

    endpoint = INSTANCE_ENDPOINTS["instance_id_path"].format(
        team_id=config.team_id, project_id=config.project_id, instance_id=instance_id
    )
    logger.info("Delete endpoint: %s", endpoint)

    response = api_client.delete(endpoint)
    logger.info("Delete response: %s", response)

    assert_response_exists(response)
    assert_schema(response.json(), "common/delete_schema.json")


def ensure_status(instance, expected_status, config, api_client):
    """
    Ensure instance reaches the expected status (running / stopped).
    """

    expected_status = expected_status.lower()

    STATE_ACTION_MAP = {
        "ready": "start",
        "stopped": "stop",
    }

    if expected_status not in STATE_ACTION_MAP:
        pytest.fail(f"Unsupported expected status: {expected_status}")

    start_time = time.time()

    while time.time() - start_time < MAX_WAIT_TIME:
        current_status = get_status(instance, config, api_client)
        logging.info(f"Current instance status: {current_status}")

        # Already in desired state
        if current_status == expected_status:
            return

        # Transitional states → just wait
        if current_status in {"waiting", "starting", "stopping"}:
            time.sleep(POLL_INTERVAL)
            continue

        # Decide action based on desired state
        action = STATE_ACTION_MAP[expected_status]

        logging.info(f"Triggering action '{action}' to reach state '{expected_status}'")
        trigger_instance_action(instance, action, config, api_client)

        time.sleep(POLL_INTERVAL)

    pytest.fail(
        f"Instance did not reach '{expected_status}' state within {MAX_WAIT_TIME}s"
    )


def trigger_instance_action(instance, action, config, api_client):
    """
    Helper function to trigger instance actions (start/stop).
    """

    params = {"action": action}
    response = api_client.put(
        INSTANCE_ENDPOINTS["instance_actions"].format(
            team_id=config.team_id, project_id=config.project_id, instance_id=instance
        ),
        params=params,
    )

    if response.status_code != 200:
        raise Exception(f"Failed to trigger action '{action}' on instance {instance}.")


def get_status(instance, config, api_client):
    """
    Helper function to get current status of instance.
    """

    response = api_client.get(
        INSTANCE_ENDPOINTS["instance_id_path"].format(
            team_id=config.team_id, project_id=config.project_id, instance_id=instance
        )
    )

    if response.status_code == 200:
        return response.json()["data"]["status"]

    raise Exception(f"Failed to fetch instance {instance} overview.")


def get_sfs_list(instance, config, api_client):
    """
    Helper function to get list of SFS mounted on instance.
    """

    response = api_client.get( INSTANCE_ENDPOINTS["mount_sfs"].format(team_id=config.team_id, project_id=config.project_id, instance_id=instance))

    if response.status_code == 200:
        return response.json()

    raise Exception(f"Failed to fetch instance {instance} overview.")

def is_sfs_mounted(instance, sfs_id, config, api_client):
    sfs_list = get_sfs_list(instance, config, api_client)
    for dataset in sfs_list["data"]:
        if dataset["id"] == sfs_id:
            return dataset["is_mounted"]

    raise AssertionError(f"Dataset with id {sfs_id} not found")

