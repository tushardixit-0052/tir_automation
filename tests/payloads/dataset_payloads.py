from datetime import datetime


def create_disk_dataset_payload(
    name: str | None = None,
    storage_type: str = "pvc",
    disk_size: int = 100,
    pvc_type: str = "custom_pvc",
    encryption_enable: bool = False,
    encryption_type: str | None = None,
):
    """
    Returns payload for dataset creation.
    """

    if not name:
        name = f"pytest-dataset-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    payload = {
        "name": name,
        "storage_type": storage_type,
        "encryption_enable": encryption_enable,
        "encryption_type": encryption_type,
    }

    if storage_type == "pvc":
        payload["pvc"] = {"disk_size": disk_size, "pvc_type": pvc_type}

    return payload
