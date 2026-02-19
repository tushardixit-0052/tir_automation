from api.paths import RESERVE_IP_ENDPOINTS
from assertions.common_assert import assert_response_exists, assert_schema
import time, pytest, logging

def reserve_new_ip(api_client, config):

    response = api_client.post(
        RESERVE_IP_ENDPOINTS["create_reserved_ip"].format(
            team_id=config.team_id, project_id=config.project_id
        )
    )

    assert_response_exists(response)
    assert_schema(response.json(), "reserveip/create_reserved_ip.json")

    return response.json()["data"]["id"]

def delete_reserved_ip(api_client, config, reserved_ip_id):

    response = api_client.delete(
        RESERVE_IP_ENDPOINTS["reserved_ip_id_path"].format(
            team_id=config.team_id, project_id=config.project_id, reserved_ip_id=reserved_ip_id
        )
    )

    assert_response_exists(response)
    assert_schema(response.json(), "reserveip/delete_reserve_ip.json")
