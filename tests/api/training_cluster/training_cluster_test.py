import pytest
import logging
from api.paths import TRAINING_CLUSTER_ENDPOINTS
from api.training_cluster.helper import (
    get_cluster_plans,
    get_training_images,
    ensure_job_running,
)
from assertions.common_assert import assert_response_exists, assert_schema

logger = logging.getLogger(__name__)


@pytest.mark.training_cluster
def test_list_cluster_plans(api_client, config):
    plans = get_cluster_plans(api_client, config)
    assert plans is not None


@pytest.mark.training_cluster
def test_list_training_images(api_client, config):
    images = get_training_images(api_client, config)
    assert images is not None


@pytest.mark.training_cluster
def test_list_clusters(api_client, config):
    endpoint = TRAINING_CLUSTER_ENDPOINTS["list_clusters"].format(
        team_id=config.team_id, project_id=config.project_id
    )
    response = api_client.get(endpoint)
    assert_response_exists(response)
    assert_schema(response.json(), "training_cluster/list_clusters.json")


@pytest.mark.training_cluster
def test_cluster_detail(api_client, config, training_cluster):
    endpoint = TRAINING_CLUSTER_ENDPOINTS["cluster_detail"].format(
        team_id=config.team_id, project_id=config.project_id, cluster_id=training_cluster
    )
    response = api_client.get(endpoint)
    assert_response_exists(response)
    assert_schema(response.json(), "training_cluster/cluster_detail.json")


@pytest.mark.training_cluster
def test_list_jobs(api_client, config):
    endpoint = TRAINING_CLUSTER_ENDPOINTS["list_jobs"].format(
        team_id=config.team_id, project_id=config.project_id
    )
    response = api_client.get(endpoint)
    assert_response_exists(response)
    assert_schema(response.json(), "training_cluster/list_jobs.json")


@pytest.mark.training_cluster
def test_job_detail(api_client, config, training_cluster, training_job):
    endpoint = TRAINING_CLUSTER_ENDPOINTS["job_detail"].format(
        team_id=config.team_id, project_id=config.project_id, job_id=training_job
    )
    response = api_client.get(endpoint)
    assert_response_exists(response)
    assert_schema(response.json(), "training_cluster/job_detail.json")


@pytest.mark.training_cluster
def test_terminate_job(api_client, config, training_cluster, training_job):
    ensure_job_running(api_client, config, training_job, logger)

    endpoint = TRAINING_CLUSTER_ENDPOINTS["terminate_job"].format(
        team_id=config.team_id, project_id=config.project_id, job_id=training_job
    )
    response = api_client.put(endpoint, params={"action": "terminate"})
    assert_response_exists(response)
    assert_schema(response.json(), "training_cluster/terminate_job.json")
