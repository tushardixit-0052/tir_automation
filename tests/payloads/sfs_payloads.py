from datetime import datetime
from constants import constant


def create_sfs_payload(
    name: str | None = None,
    disk_size: int = constant.DEFAULT_SFS_SIZE,
):
    """
    Returns payload for file system creation.
    """

    if not name:
        name = f"pytest-file-system-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    payload = {
        "name": name,
        "disk_size": disk_size,
    }

    return payload
