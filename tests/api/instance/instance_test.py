# tests/api/nodes.py
import pytest, time, json, logging
from api.paths import INSTANCE_ENDPOINTS
from api.instance.helper import ensure_status, is_sfs_mounted
from assertions.common_assert import assert_response_exists, assert_schema
from payloads import instance_payloads
from api.securitygroup.helper import get_security_group_listing

# from instance.instance_fixtures import instance

logger = logging.getLogger(__name__)


@pytest.mark.instance
def test_list_node_images(api_client):

    response = api_client.get(INSTANCE_ENDPOINTS["list_instance_images"])

    assert_response_exists(response)
    assert_schema(response.json(), "instance/image_list.json")


@pytest.mark.instance
def test_sku_list(api_client):

    params = {"service": "notebook", "location": "Delhi"}
    response = api_client.get(INSTANCE_ENDPOINTS["sku_list_notebook"], params=params)
    # logger.info(f"Response JSON: {response.json()}")

    assert_response_exists(response)
    assert_schema(response.json(), "instance/sku_list.json")


# @pytest.mark.instance
# def test_instance_lifecycle(instance):
#     assert instance is not None


@pytest.mark.instance
def test_overview(api_client, instance, config):
    response = api_client.get(
        INSTANCE_ENDPOINTS["instance_id_path"].format(
            team_id=config.team_id, project_id=config.project_id, instance_id=instance
        )
    )

    assert_response_exists(response)
    assert_schema(response.json(), "instance/instance_overview.json")


@pytest.mark.instance
def test_instance_events(api_client, instance, config):
    # ensure instance is in running state before fetching events

    ensure_status(instance, "ready", config, api_client)
    response = api_client.get(
        INSTANCE_ENDPOINTS["instace_events"].format(
            team_id=config.team_id, project_id=config.project_id, instance_id=instance
        )
    )

    assert_response_exists(response)
    assert_schema(response.json(), "instance/instance_events.json")


# @pytest.mark.instance
# def test_monitoring(api_client, instance):

@pytest.mark.instance
def test_update_workspace(api_client, instance, config):
    time.sleep(3)
    payload = {"size": 40}
    response = api_client.put(INSTANCE_ENDPOINTS["upgrade_workspace_size"].format(team_id=config.team_id, project_id=config.project_id, instance_id=instance), data=payload)

    assert_response_exists(response)
    assert_schema(response.json(), "instance/instance_overview.json")

@pytest.mark.instance
def test_stop_instance(api_client, instance, config):
    # ensure instance is in running state before stopping
    ensure_status(instance, "ready", config, api_client)
    params = {"action": "stop"}
    response = api_client.put(INSTANCE_ENDPOINTS["instance_actions"].format(team_id=config.team_id, project_id=config.project_id, instance_id=instance), params=params)

    assert_response_exists(response)
    assert_schema(response.json(), "instance/instance_stop_action.json")

@pytest.mark.instance
def test_update_plan(api_client, instance, config):
    #ensure node is in stopped state before updating plan
    # time.sleep(60)
    ensure_status(instance, "stopped", config, api_client)
    payload = instance_payloads.update_instance_sku_payload()
    response = api_client.put(INSTANCE_ENDPOINTS["instance_id_path"].format(team_id=config.team_id, project_id=config.project_id, instance_id=instance), data=payload)

    assert_response_exists(response)
    assert_schema(response.json(), "instance/instance_overview.json")

# after plan update instance came into start state
@pytest.mark.instance
def test_start_instance(api_client, instance, config):
    # ensure instance is in stopped state before starting
    ensure_status(instance, "stopped", config, api_client)
    params = {"action": "start"}
    response = api_client.put(INSTANCE_ENDPOINTS["instance_actions"].format(team_id=config.team_id, project_id=config.project_id, instance_id=instance), params=params)

    assert_response_exists(response)
    assert_schema(response.json(), "instance/instance_start_action.json")

@pytest.mark.instance
def test_restart_instance(api_client, instance, config):
    # ensure instance is in running state before restarting
    # time.sleep(60)
    ensure_status(instance, "ready", config, api_client)
    params = {"action": "restart"}
    response = api_client.put(INSTANCE_ENDPOINTS["instance_actions"].format(team_id=config.team_id, project_id=config.project_id, instance_id=instance), params=params)

    assert_response_exists(response)
    assert_schema(response.json(), "instance/instance_restart_action.json")

@pytest.mark.instance
def test_update_image(api_client, instance, config):
    # ensure instance is in running or stopped state before updating image
    # ensure that if you are converting it to the base os then ssh is enabled
    # time.sleep(60)
    ensure_status(instance, "ready", config, api_client)
    payload = instance_payloads.update_instance_image_payload()
    response = api_client.put(INSTANCE_ENDPOINTS["image_update"].format(team_id=config.team_id, project_id=config.project_id, instance_id=instance), data=payload)

    assert_response_exists(response)
    assert_schema(response.json(), "instance/update_image.json")
    logger.info("test update image done")

@pytest.mark.instance
def test_convert_to_committed(api_client, instance, config):
    # ensure instance is in running or stopped state before updating image
    time.sleep(3)

    ensure_status(instance, "ready", config, api_client)
    payload = instance_payloads.update_committed_instance_payload()
    response = api_client.put(INSTANCE_ENDPOINTS["instance_id_path"].format(team_id=config.team_id, project_id=config.project_id, instance_id=instance), data=payload)

    assert_response_exists(response)
    assert_schema(response.json(), "instance/instance_overview.json")

    data = response.json()["data"]
    # sku correctness
    assert data["sku_details"]["specs"]["sku_id"] == payload["sku_id"]
    assert data["sku_details"]["plan"]["sku_type"] == "committed"

# @pytest.mark.instance
# def test_update_committed_hourly_policy(api_client, instance, config):
#     # ensure instance is in running or stopped state before updating image
#     time.sleep(3)

#     ensure_status(instance, "stopped", config, api_client)
#     payload = instance_payloads.update_committed_instance_payload(committed_instance_policy="convert_to_hourly_billing", next_sku_item_price_id=4)
#     response = api_client.put(INSTANCE_ENDPOINTS["instance_id_path"].format(team_id=config.team_id, project_id=config.project_id, instance_id=instance), data=payload)

#     assert_response_exists(response)
#     assert_schema(response.json(), "instance/instance_overview.json")

#     data = response.json()["data"]
#     committed_info = data["committed_info"]

#     assert committed_info["updation_policy"] == payload["committed_instance_policy"]
#         # sku correctness
#     assert data["sku_details"]["specs"]["sku_id"] == payload["sku_id"]

# @pytest.mark.instance
# def test_update_committed_auto_delete_policy(api_client, instance, config):
#     # ensure instance is in running or stopped state before updating image
#     time.sleep(3)

#     ensure_status(instance, "stopped", config, api_client)
#     payload = instance_payloads.update_committed_instance_payload(committed_instance_policy="auto_terminate", next_sku_item_price_id=None)
#     response = api_client.put(INSTANCE_ENDPOINTS["instance_id_path"].format(team_id=config.team_id, project_id=config.project_id, instance_id=instance), data=payload)

#     assert_response_exists(response)
#     assert_schema(response.json(), "instance/instance_overview.json")

#     data = response.json()["data"]
#     committed_info = data["committed_info"]

#     assert committed_info["updation_policy"] == payload["committed_instance_policy"]
#         # sku correctness
#     assert data["sku_details"]["specs"]["sku_id"] == payload["sku_id"]


@pytest.mark.instance
def test_mount_dataset(api_client, instance, config, dataset):

    dataset_id = dataset["id"]
    dataset_name = dataset["name"]
    payload = instance_payloads.dataset_payload(mount_ids=[dataset_id])
    logger.info(f"Mounting dataset with payload: {json.dumps(payload)}")

    response = api_client.put(
        INSTANCE_ENDPOINTS["dataset"].format(
            team_id=config.team_id, project_id=config.project_id, instance_id=instance
        ),
        data=payload,
    )

    assert_response_exists(response)
    assert_schema(response.json(), "instance/dataset_mount_unmount.json")
    mounted = response.json()["data"]["mounted_datasets"]
    unmounted = response.json()["data"]["unmounted_datasets"]
    assert dataset_name in mounted
    assert dataset_name not in unmounted


@pytest.mark.instance
def test_unmount_dataset(api_client, instance, config, dataset):

    dataset_id = dataset["id"]
    dataset_name = dataset["name"]
    payload = instance_payloads.dataset_payload(unmount_ids=[dataset_id])
    response = api_client.put(
        INSTANCE_ENDPOINTS["dataset"].format(
            team_id=config.team_id, project_id=config.project_id, instance_id=instance
        ),
        data=payload,
    )

    assert_response_exists(response)
    assert_schema(response.json(), "instance/dataset_mount_unmount.json")
    mounted = response.json()["data"]["mounted_datasets"]
    unmounted = response.json()["data"]["unmounted_datasets"]
    assert dataset_name not in mounted
    assert dataset_name in unmounted


@pytest.mark.instance
def test_mount_sfs(api_client, instance, config, sfs):

    sfs_id = sfs
    payload = instance_payloads.sfs_action_payload("mount", sfs_ids=[sfs_id])
    logger.info(f"Mounting SFS with payload: {json.dumps(payload)}")

    response = api_client.put(
        INSTANCE_ENDPOINTS["mount_sfs"].format(
            team_id=config.team_id, project_id=config.project_id, instance_id=instance
        ),
        data=payload,
    )

    assert_response_exists(response)
    assert_schema(response.json(), "common/success_200.json")

    #verify that sfs is in mounted list and is_mounted field is true
    mounted_status = is_sfs_mounted(instance, sfs_id, config, api_client)
    assert mounted_status is True

@pytest.mark.instance
def test_unount_sfs(api_client, instance, config, sfs):
    sfs_id = sfs
    payload = instance_payloads.sfs_action_payload("unmount", sfs_ids=[sfs_id])
    logger.info(f"Unmounting SFS with payload: {json.dumps(payload)}")

    response = api_client.put(
        INSTANCE_ENDPOINTS["mount_sfs"].format(
            team_id=config.team_id, project_id=config.project_id, instance_id=instance
        ),
        data=payload,
    )

    assert_response_exists(response)
    assert_schema(response.json(), "common/success_200.json")

    #verify that sfs is in unmounted list and is_mounted field is false
    mounted_status = is_sfs_mounted(instance, sfs_id, config, api_client)
    assert mounted_status is False

# @pytest.mark.instance
#     def test_mount_pfs(api_client, instance, config):

# @pytest.mark.instance
#     def test_unmount_pfs(api_client, instance, config):

# @pytest.mark.instance
# def test_attach_security_group(api_client, instance, config):
    
#     security_group_list = get_security_group_listing(api_client, config)
#     assert len(security_group_list["data"]) > 0, "No security groups available to attach"
#     security_group_id = security_group_list["data"][0]["id"]

#     payload = instance_payloads.security_group_payload(security_group_ids=[security_group_id])
#     logger.info(f"Attaching security group with payload: {json.dumps(payload)}")

#     response = api_client.post(
#         INSTANCE_ENDPOINTS["attach_security_group"].format(
#             team_id=config.team_id, project_id=config.project_id, instance_id=instance
#         ),
#         data=payload,
#     )

#     assert_response_exists(response)
#     assert_schema(response.json(), "instance/attach_security_group.json")

# @pytest.mark.instance
#     def test_attach_ssh_key(api_client, instance, config):

@pytest.mark.instance
def test_reserve_ip(api_client, instance, config, reserved_ip):
    reserved_ip_id = reserved_ip
    params = {"action": "attach_reserve_ip"}

    payload = instance_payloads.reserve_ip_payload(reserved_ip_id=reserved_ip_id)
    logger.info(f"Attaching reserved IP with payload: {json.dumps(payload)}")

    response = api_client.put(
        INSTANCE_ENDPOINTS["instance_actions"].format(
            team_id=config.team_id, project_id=config.project_id, instance_id=instance
        ), 
        data=payload, params=params
    )

    assert_response_exists(response)
    assert_schema(response.json(), "instance/reserve_ip.json")

# @pytest.mark.instance
#     def test_detach_ssh_key(api_client, instance, config):

@pytest.mark.instance
def test_unreserve_ip(api_client, instance, config, reserved_ip):
    reserved_ip_id = reserved_ip
    params = {"action": "detach_reserve_ip"}

    payload = instance_payloads.reserve_ip_payload(reserved_ip_id=reserved_ip_id)
    logger.info(f"Detaching reserved IP with payload: {json.dumps(payload)}")

    response = api_client.put(
        INSTANCE_ENDPOINTS["instance_actions"].format(
            team_id=config.team_id, project_id=config.project_id, instance_id=instance
        ), 
        data=payload, params=params
    )

    assert_response_exists(response)
    assert_schema(response.json(), "instance/detach_reserve_ip.json")


# @pytest.mark.instance
# def test_detach_security_group(api_client, instance, config):

