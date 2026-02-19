from datetime import datetime
from typing import Optional, List
from constants import constant


def create_instance_payload(
    name: str | None = None,
    image_version_id: int = 59,
    app_id: int = 3,
    sku_id: int = 4,
    sku_item_price_id: int = 4,
    disk_size_in_gb: int = 30,
    enable_ssh: bool = False,
):
    """
    Returns payload for instance creation.
    """

    if not name:
        name = f"pytest-instance-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    return {
        "name": name,
        "cluster_type": "tir-cluster",
        "image_type": "pre-built",
        "notebook_type": "new",
        "notebook_url": "",
        "disk_size_in_gb": disk_size_in_gb,
        "dataset_id_list": [],
        "enable_ssh": enable_ssh,
        "add_ons": [],
        "is_pvc_encrypted": False,
        "sfs_path": "/mnt/sfs",
        "pfs_path": "/mnt/pfs",
        "pfs_read_only": False,
        "image_version_id": image_version_id,
        "app_id": app_id,
        "sku_id": sku_id,
        "sku_item_price_id": sku_item_price_id,
        "instance_type": "paid_usage",
    }


def update_instance_image_payload(
    image_version_id: int = 23,
    app_id: int = 3,
    image_type: str = "pre-built",
    is_jupyterlab_enabled: bool = True,
    is_advanced_search: bool = False,
):
    """
    Returns payload for notebook image update.
    """

    return {
        "image_type": image_type,
        "image_version_id": image_version_id,
        "app_id": app_id,
        "is_jupyterlab_enabled": is_jupyterlab_enabled,
        "is_advanced_search": is_advanced_search,
    }


def update_instance_sku_payload(
    sku_id: int = 16,
    sku_item_price_id: int = 54,
    cluster_type: str = "tir-cluster",
):
    """
    Returns payload for instance SKU update.
    """

    return {
        "cluster_type": cluster_type,
        "sku_id": sku_id,
        "sku_item_price_id": sku_item_price_id,
    }


def update_committed_instance_payload(
    sku_id: int = 4,
    sku_item_price_id: int = 1292,
    next_sku_item_price_id: Optional[int] = 1292,
    committed_instance_policy: str = "auto_renew",
):
    """
    Returns payload for committed instance / plan update.
    """

    return {
        "committed_instance_policy": committed_instance_policy,
        "sku_id": sku_id,
        "sku_item_price_id": sku_item_price_id,
        "next_sku_item_price_id": next_sku_item_price_id,
    }


def dataset_payload(mount_ids=None, unmount_ids=None):
    return {
        "dataset_id_dict": {
            "dataset_ids_to_mount": mount_ids or [],
            "dataset_ids_to_unmount": unmount_ids or [],
        }
    }


def sfs_action_payload(
    action: str,
    sfs_ids: List[int],
):

    if action not in ["mount", "unmount"]:
        raise ValueError("Action must be either 'mount' or 'unmount'")

    payload = {
        "action": action,
        "sfs_ids": sfs_ids,
    }

    if action == "mount":
        payload["sfs_path"] = constant.SFS_MOUNT_PATH

    return payload

def security_group_payload(security_group_ids: list[int]):
    return {
        "security_groups_ids": security_group_ids
    }

def reserve_ip_payload(reserved_ip_id: int ):
    return {
        "reserved_ip_id": reserved_ip_id
    }

