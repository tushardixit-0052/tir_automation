from api.paths import SECURITY_GROUP_ENDPOINTS

def get_security_group_listing(api_client, config):
    response = api_client.get(SECURITY_GROUP_ENDPOINTS["list_security_groups"].format(team_id=config.team_id, project_id=config.project_id))
    return response.json()