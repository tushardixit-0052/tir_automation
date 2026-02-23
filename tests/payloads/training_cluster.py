from datetime import datetime
from typing import Optional, List


def create_cluster_payload(
    name: str | None = None,
    plan_id: int = 1,
    node_count: int = 1,
) -> dict:
    """Returns payload for training cluster creation."""
    if not name:
        name = f"pytest-cluster-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    return {
        "name": name,
        "plan_id": plan_id,
        "node_count": node_count,
    }


def create_job_payload(
    cluster_id: int,
    image_url: str,
    name: str | None = None,
    command: str = "echo 'hello from pytest job'",
    num_workers: int = 1,
    framework: str = "pytorch",
    env_variables: Optional[List[dict]] = None,
) -> dict:
    """Returns payload for deployment/job creation on a training cluster."""
    if not name:
        name = f"pytest-job-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    return {
        "name": name,
        "cluster_id": cluster_id,
        "image_url": image_url,
        "command": command,
        "num_workers": num_workers,
        "framework": framework,
        "env_variables": env_variables or [],
    }
