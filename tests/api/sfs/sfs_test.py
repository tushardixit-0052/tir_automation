import pytest
import json
import logging
from api.paths import SFS_ENDPOINTS, INSTANCE_ENDPOINTS
from api.sfs.helper import list_sfs, list_attached_notebooks
from api.instance.helper import ensure_status, is_sfs_mounted
from assertions.common_assert import assert_response_exists, assert_schema
from payloads import instance_payloads

logger = logging.getLogger(__name__)


@pytest.mark.sfs
def test_list_sfs(api_client, config, sfs):
    """List all SFS in the project and verify the created SFS is present."""
    sfs_id = sfs

    response_json = list_sfs(api_client, config, logger)

    assert_schema(response_json, "sfs/list_sfs.json")

    sfs_ids_in_list = [item["id"] for item in response_json["data"]]
    assert sfs_id in sfs_ids_in_list, f"Created SFS {sfs_id} not found in list: {sfs_ids_in_list}"
    logger.info("SFS %s found in list", sfs_id)


@pytest.mark.sfs
def test_mount_sfs(api_client, instance, config, sfs):
    """Mount the SFS to a running instance and verify mount status."""
    sfs_id = sfs

    ensure_status(instance, "ready", config, api_client)

    payload = instance_payloads.sfs_action_payload("mount", sfs_ids=[sfs_id])
    logger.info("Mounting SFS with payload: %s", json.dumps(payload))

    response = api_client.put(
        INSTANCE_ENDPOINTS["mount_sfs"].format(
            team_id=config.team_id, project_id=config.project_id, instance_id=instance
        ),
        data=payload,
    )

    assert_response_exists(response)
    assert_schema(response.json(), "common/success_200.json")

    mounted_status = is_sfs_mounted(instance, sfs_id, config, api_client)
    assert mounted_status is True, f"SFS {sfs_id} should be mounted on instance {instance}"
    logger.info("SFS %s successfully mounted to instance %s", sfs_id, instance)


@pytest.mark.sfs
def test_list_attached_resources(api_client, config, sfs, instance):
    """List notebooks attached to the SFS and verify the instance appears after mount."""
    sfs_id = sfs

    response_json = list_attached_notebooks(api_client, config, sfs_id, logger)

    assert_schema(response_json, "sfs/list_attached_notebooks.json")

    assert response_json["total_count"] >= 1, "Expected at least one attached notebook after mounting"

    attached_ids = [item["id"] for item in response_json["data"]]
    assert instance in attached_ids, f"Instance {instance} not found in attached notebooks: {attached_ids}"

    mounted_item = next(item for item in response_json["data"] if item["id"] == instance)
    assert mounted_item["is_mounted"] is True, f"Instance {instance} is_mounted should be True"
    logger.info("Instance %s found in attached resources for SFS %s", instance, sfs_id)


@pytest.mark.sfs
def test_unmount_sfs(api_client, instance, config, sfs):
    """Unmount the SFS from the instance and verify unmount status."""
    sfs_id = sfs

    payload = instance_payloads.sfs_action_payload("unmount", sfs_ids=[sfs_id])
    logger.info("Unmounting SFS with payload: %s", json.dumps(payload))

    response = api_client.put(
        INSTANCE_ENDPOINTS["mount_sfs"].format(
            team_id=config.team_id, project_id=config.project_id, instance_id=instance
        ),
        data=payload,
    )

    assert_response_exists(response)
    assert_schema(response.json(), "common/success_200.json")

    mounted_status = is_sfs_mounted(instance, sfs_id, config, api_client)
    assert mounted_status is False, f"SFS {sfs_id} should be unmounted from instance {instance}"
    logger.info("SFS %s successfully unmounted from instance %s", sfs_id, instance)
