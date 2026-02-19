import pytest, time, json, logging
from api.paths import DATASET_ENDPOINTS
from assertions.common_assert import assert_response_exists, assert_schema
from payloads import dataset_payloads

logger = logging.getLogger(__name__)


@pytest.mark.dataset
def test_dataset_lifecyle(dataset):
    assert dataset is not None
