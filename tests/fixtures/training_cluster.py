import pytest
import logging
from api.training_cluster.helper import (
    create_cluster,
    delete_cluster,
    ensure_cluster_ready,
    get_training_images,
    create_job,
    delete_job,
)

logger = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def training_cluster(api_client, config):
    cluster_id = create_cluster(api_client, config, logger)
    ensure_cluster_ready(api_client, config, cluster_id, logger)
    yield cluster_id
    delete_cluster(api_client, config, cluster_id, logger)


@pytest.fixture(scope="module")
def training_job(api_client, config, training_cluster):
    images = get_training_images(api_client, config)
    if not images:
        pytest.skip("No training images available to create a deployment")

    image_url = images[0].get("image_url", "")
    job_id = create_job(api_client, config, training_cluster, image_url, logger)
    yield job_id
    delete_job(api_client, config, job_id, logger)
