import pytest
import json
import logging
from api.paths import SFS_ENDPOINTS, INSTANCE_ENDPOINTS
from api.sfs.helper import create_sfs, delete_sfs, list_attached_notebooks
from api.instance.helper import ensure_status
from assertions.common_assert import assert_schema
from payloads import instance_payloads
from constants import constant

logger = logging.getLogger(__name__)

FAKE_SFS_ID = 999999999


# ── HELPERS ───────────────────────────────────────────────────────────────────


def _mount_endpoint(config, instance_id):
    return INSTANCE_ENDPOINTS["mount_sfs"].format(
        team_id=config.team_id, project_id=config.project_id, instance_id=instance_id
    )


# ── CREATE SFS ────────────────────────────────────────────────────────────────


@pytest.mark.sfs
def test_create_sfs_without_name(api_client, config):
    """POST without 'name' field — API returns 412 with field-level error."""
    endpoint = SFS_ENDPOINTS["create_sfs"].format(
        team_id=config.team_id, project_id=config.project_id
    )
    response = api_client.raw_post(endpoint, data={"disk_size": 500})

    assert response.status_code == 412, f"Expected 412, got {response.status_code}"
    body = response.json()
    assert_schema(body, "common/error_412.json")
    assert "name" in body["errors"], f"Expected 'name' error, got: {body['errors']}"


@pytest.mark.sfs
def test_create_sfs_without_disk_size(api_client, config):
    """POST without 'disk_size' field — API returns 412 with field-level error."""
    endpoint = SFS_ENDPOINTS["create_sfs"].format(
        team_id=config.team_id, project_id=config.project_id
    )
    response = api_client.raw_post(endpoint, data={"name": "pytest-neg-sfs-no-disk"})

    assert response.status_code == 412, f"Expected 412, got {response.status_code}"
    body = response.json()
    assert_schema(body, "common/error_412.json")
    assert "disk_size" in body["errors"], (
        f"Expected 'disk_size' error, got: {body['errors']}"
    )


@pytest.mark.sfs
def test_create_sfs_empty_payload(api_client, config):
    """POST with empty body — API returns 412 with errors for both required fields."""
    endpoint = SFS_ENDPOINTS["create_sfs"].format(
        team_id=config.team_id, project_id=config.project_id
    )
    response = api_client.raw_post(endpoint, data={})

    assert response.status_code == 412, f"Expected 412, got {response.status_code}"
    body = response.json()
    assert_schema(body, "common/error_412.json")
    assert "name" in body["errors"], f"Expected 'name' error, got: {body['errors']}"
    assert "disk_size" in body["errors"], (
        f"Expected 'disk_size' error, got: {body['errors']}"
    )


# ── DELETE SFS ────────────────────────────────────────────────────────────────


@pytest.mark.sfs
def test_delete_nonexistent_sfs(api_client, config):
    """DELETE with a non-existent SFS ID — API returns 404 with string error message."""
    endpoint = SFS_ENDPOINTS["sfs_id_path"].format(
        team_id=config.team_id, project_id=config.project_id, sfs_id=FAKE_SFS_ID
    )
    response = api_client.raw_delete(endpoint)

    assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    body = response.json()
    assert_schema(body, "common/error_404.json")
    assert "does not exist" in body["errors"].lower(), (
        f"Expected 'does not exist' in errors, got: {body['errors']}"
    )


# ── LIST ATTACHED NOTEBOOKS ───────────────────────────────────────────────────


@pytest.mark.sfs
def test_list_attached_notebooks_nonexistent_sfs(api_client, config):
    """
    GET attached notebooks for a non-existent SFS ID.

    NOTE: The API currently returns 200 with empty data instead of 404.
    This is a known API limitation. The test asserts the current behaviour
    (empty list, total_count=0) so it fails if the API silently returns
    data for a non-existent resource.
    """
    response_json = list_attached_notebooks(api_client, config, FAKE_SFS_ID, logger)

    assert response_json["code"] == 200
    assert response_json["data"] == [], (
        f"Expected empty data for non-existent SFS, got: {response_json['data']}"
    )
    assert response_json["total_count"] == 0, (
        f"Expected total_count=0 for non-existent SFS, got: {response_json['total_count']}"
    )


# ── MOUNT / UNMOUNT SFS ───────────────────────────────────────────────────────


@pytest.mark.sfs
def test_mount_nonexistent_sfs_to_instance(api_client, instance, config):
    """Mounting a non-existent SFS ID to a valid instance should fail."""
    ensure_status(instance, "ready", config, api_client)

    payload = instance_payloads.sfs_action_payload("mount", sfs_ids=[FAKE_SFS_ID])
    logger.info(
        "Attempting to mount non-existent SFS %s to instance %s", FAKE_SFS_ID, instance
    )

    with pytest.raises(Exception) as exc:
        api_client.put(_mount_endpoint(config, instance), data=payload)
    assert any(code in str(exc.value) for code in ["400", "404"]), (
        f"Expected 400 or 404, got: {exc.value}"
    )


@pytest.mark.sfs
def test_mount_sfs_with_invalid_action(api_client, instance, config, sfs):
    """Sending an unrecognised action value — API returns 412 with 'Invalid action' error."""
    ensure_status(instance, "ready", config, api_client)

    # Construct payload manually — the payload builder validates action locally
    payload = {
        "action": "launch",
        "sfs_ids": [sfs],
        "sfs_path": constant.SFS_MOUNT_PATH,
    }
    logger.info("Attempting mount with invalid action: %s", json.dumps(payload))

    response = api_client.raw_put(_mount_endpoint(config, instance), data=payload)
    body = response.json()

    assert response.status_code == 412, f"Expected 412, got: {response.status_code}"
    assert_schema(body, "sfs/error_412_string.json")
    assert body["errors"] == "Invalid action", (
        f"Expected 'Invalid action' error, got: {body['errors']}"
    )
    logger.info(
        "test_mount_sfs_with_invalid_action passed — errors: %s", body["errors"]
    )


@pytest.mark.sfs
def test_mount_sfs_with_empty_sfs_ids(api_client, instance, config):
    """Mounting with an empty sfs_ids list should be rejected."""
    ensure_status(instance, "ready", config, api_client)

    payload = {
        "action": "mount",
        "sfs_ids": [],
        "sfs_path": constant.SFS_MOUNT_PATH,
    }
    logger.info("Attempting mount with empty sfs_ids: %s", json.dumps(payload))

    with pytest.raises(Exception) as exc:
        api_client.put(_mount_endpoint(config, instance), data=payload)
    assert "400" in str(exc.value), f"Expected 400, got: {exc.value}"


@pytest.mark.sfs
def test_mount_two_sfs_on_same_path(api_client, instance, config, sfs):
    """
    Mounting a second SFS on a path already occupied by another SFS should fail.
    Steps:
      1. Mount sfs (fixture) to SFS_MOUNT_PATH (/test)
      2. Create a second SFS inline
      3. Attempt to mount second SFS to the same path → expect 400
      4. Cleanup: unmount first SFS, delete second SFS
    """
    ensure_status(instance, "ready", config, api_client)
    endpoint = _mount_endpoint(config, instance)

    # Step 1: mount the fixture SFS to the default path
    mount_payload = instance_payloads.sfs_action_payload("mount", sfs_ids=[sfs])
    logger.info("Mounting first SFS %s to path %s", sfs, constant.SFS_MOUNT_PATH)
    api_client.put(endpoint, data=mount_payload)

    # Step 2: create a second SFS to use as the conflicting mount
    second_sfs_id = create_sfs(api_client, config, logger)
    logger.info("Created second SFS %s for conflict test", second_sfs_id)

    try:
        # Step 3: try mounting second SFS to the same path — should fail
        conflict_payload = {
            "action": "mount",
            "sfs_ids": [second_sfs_id],
            "sfs_path": constant.SFS_MOUNT_PATH,  # same path as first SFS
        }
        logger.info(
            "Attempting to mount second SFS %s to already-occupied path %s",
            second_sfs_id,
            constant.SFS_MOUNT_PATH,
        )
        response = api_client.raw_put(endpoint, data=conflict_payload)
        body = response.json()

        assert response.status_code == 412, (
            f"Expected 412 when mounting to an occupied path, got: {response.status_code}"
        )
        assert_schema(body, "sfs/error_412_string.json")
        assert body["errors"] == "file system path already mounted", (
            f"Expected 'file system path already mounted' error, got: {body['errors']}"
        )
        logger.info(
            "test_mount_two_sfs_on_same_path passed — errors: %s", body["errors"]
        )
    finally:
        # Step 4: unmount the first SFS so fixture teardown can delete it cleanly
        try:
            unmount_payload = instance_payloads.sfs_action_payload(
                "unmount", sfs_ids=[sfs]
            )
            api_client.put(endpoint, data=unmount_payload)
            logger.info("Unmounted first SFS %s during cleanup", sfs)
        except Exception as e:
            logger.warning("Could not unmount first SFS %s during cleanup: %s", sfs, e)

        # Delete the second SFS created inline
        delete_sfs(api_client, config, second_sfs_id, logger)
