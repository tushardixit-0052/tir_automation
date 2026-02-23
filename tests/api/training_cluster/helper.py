from payloads import training_cluster as tc_payloads
from api.paths import TRAINING_CLUSTER_ENDPOINTS
from assertions.common_assert import assert_response_exists, assert_schema
import time, pytest, logging

POLL_INTERVAL = 15
MAX_WAIT_TIME = 600  # seconds – clusters take longer to provision

logger = logging.getLogger(__name__)

CLUSTER_READY_STATES = {"running", "active"}
CLUSTER_TERMINAL_STATES = {"failed", "error"}

JOB_READY_STATES = {"running", "completed"}
JOB_TERMINAL_STATES = {"failed", "error", "terminated"}


# ─── Cluster Helpers ──────────────────────────────────────────────────────────

def get_cluster_plans(api_client, config):
    endpoint = TRAINING_CLUSTER_ENDPOINTS["list_cluster_plans"].format(
        team_id=config.team_id, project_id=config.project_id
    )
    response = api_client.get(endpoint)
    assert_response_exists(response)
    assert_schema(response.json(), "training_cluster/cluster_plans.json")
    return response.json()["data"]


def create_cluster(api_client, config, logger, plan_id: int = 1, node_count: int = 1):
    logger.info("Creating training cluster")

    endpoint = TRAINING_CLUSTER_ENDPOINTS["create_cluster"].format(
        team_id=config.team_id, project_id=config.project_id
    )
    payload = tc_payloads.create_cluster_payload(plan_id=plan_id, node_count=node_count)
    logger.info("Create cluster payload: %s", payload)

    response = api_client.post(endpoint, data=payload)
    assert_response_exists(response)
    assert_schema(response.json(), "training_cluster/create_cluster.json")

    cluster_id = response.json()["data"]["id"]
    logger.info("Created training cluster with ID: %s", cluster_id)
    return cluster_id


def delete_cluster(api_client, config, cluster_id, logger):
    logger.info("Deleting training cluster %s", cluster_id)

    endpoint = TRAINING_CLUSTER_ENDPOINTS["delete_cluster"].format(
        team_id=config.team_id, project_id=config.project_id, cluster_id=cluster_id
    )
    response = api_client.delete(endpoint)
    assert_response_exists(response)
    assert_schema(response.json(), "training_cluster/delete_cluster.json")
    logger.info("Deleted training cluster %s", cluster_id)


def get_cluster_status(api_client, config, cluster_id) -> str:
    endpoint = TRAINING_CLUSTER_ENDPOINTS["cluster_detail"].format(
        team_id=config.team_id, project_id=config.project_id, cluster_id=cluster_id
    )
    response = api_client.get(endpoint)
    if response.status_code == 200:
        return response.json()["data"]["status"].lower()
    raise Exception(f"Failed to fetch cluster {cluster_id} status.")


def ensure_cluster_ready(api_client, config, cluster_id, logger):
    logger.info("Waiting for cluster %s to become ready", cluster_id)

    start_time = time.time()
    while time.time() - start_time < MAX_WAIT_TIME:
        status = get_cluster_status(api_client, config, cluster_id)
        logger.info("Cluster %s status: %s", cluster_id, status)

        if status in CLUSTER_READY_STATES:
            return
        if status in CLUSTER_TERMINAL_STATES:
            pytest.fail(f"Cluster {cluster_id} entered terminal state: {status}")

        time.sleep(POLL_INTERVAL)

    pytest.fail(f"Cluster {cluster_id} did not become ready within {MAX_WAIT_TIME}s")


# ─── Image Helpers ────────────────────────────────────────────────────────────

def get_training_images(api_client, config, job_type: str = "pytorch"):
    endpoint = TRAINING_CLUSTER_ENDPOINTS["list_training_images"].format(
        team_id=config.team_id, project_id=config.project_id
    )
    response = api_client.get(endpoint, params={"job_type": job_type})
    assert_response_exists(response)
    assert_schema(response.json(), "training_cluster/training_images.json")
    return response.json()["data"]


# ─── Job / Deployment Helpers ─────────────────────────────────────────────────

def create_job(api_client, config, cluster_id, image_url, logger):
    logger.info("Creating deployment on cluster %s", cluster_id)

    endpoint = TRAINING_CLUSTER_ENDPOINTS["create_job"].format(
        team_id=config.team_id, project_id=config.project_id
    )
    payload = tc_payloads.create_job_payload(cluster_id=cluster_id, image_url=image_url)
    logger.info("Create job payload: %s", payload)

    response = api_client.post(endpoint, data=payload)
    assert_response_exists(response)
    assert_schema(response.json(), "training_cluster/create_job.json")

    job_id = response.json()["data"]["id"]
    logger.info("Created deployment/job with ID: %s", job_id)
    return job_id


def delete_job(api_client, config, job_id, logger):
    logger.info("Deleting deployment/job %s", job_id)

    endpoint = TRAINING_CLUSTER_ENDPOINTS["delete_job"].format(
        team_id=config.team_id, project_id=config.project_id, job_id=job_id
    )
    response = api_client.delete(endpoint)
    assert_response_exists(response)
    assert_schema(response.json(), "training_cluster/delete_job.json")
    logger.info("Deleted deployment/job %s", job_id)


def get_job_status(api_client, config, job_id) -> str:
    endpoint = TRAINING_CLUSTER_ENDPOINTS["job_detail"].format(
        team_id=config.team_id, project_id=config.project_id, job_id=job_id
    )
    response = api_client.get(endpoint)
    if response.status_code == 200:
        return response.json()["data"]["status"].lower()
    raise Exception(f"Failed to fetch job {job_id} status.")


def ensure_job_running(api_client, config, job_id, logger):
    logger.info("Waiting for job %s to start running", job_id)

    start_time = time.time()
    while time.time() - start_time < MAX_WAIT_TIME:
        status = get_job_status(api_client, config, job_id)
        logger.info("Job %s status: %s", job_id, status)

        if status in JOB_READY_STATES:
            return
        if status in JOB_TERMINAL_STATES:
            pytest.fail(f"Job {job_id} entered terminal state: {status}")

        time.sleep(POLL_INTERVAL)

    pytest.fail(f"Job {job_id} did not reach running state within {MAX_WAIT_TIME}s")
