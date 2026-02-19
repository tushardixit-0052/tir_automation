# tests/api/paths.py

INSTANCE_ENDPOINTS = {
    "list_instance_images": "/gpu_service/image/",  # GET
    "sku_list_notebook": "/gpu_service/sku/",  # GET
    "create_instance": "/teams/{team_id}/projects/{project_id}/notebooks/",  # POST
    "instance_id_path": "/teams/{team_id}/projects/{project_id}/notebooks/{instance_id}/",
    "instace_events": "/teams/{team_id}/projects/{project_id}/notebooks/{instance_id}/events/",  # GET
    "upgrade_workspace_size": "/teams/{team_id}/projects/{project_id}/notebooks/{instance_id}/pvc/upgrade/",  # PUT
    "instance_actions": "/teams/{team_id}/projects/{project_id}/notebooks/{instance_id}/actions/",  # PUT
    "image_update": "/teams/{team_id}/projects/{project_id}/notebooks/{instance_id}/image_update/",  # PUT
    "dataset": "/teams/{team_id}/projects/{project_id}/notebooks/{instance_id}/mounted-datasets/",  # PUT
    "mount_sfs": "/teams/{team_id}/projects/{project_id}/notebooks/{instance_id}/mounted-sfs/",  # PUT
    "attach_security_group": "/teams/{team_id}/projects/{project_id}/notebooks/{instance_id}/security-groups/",  # PUT
    "detach_security_group": "/teams/{team_id}/projects/{project_id}/notebooks/{instance_id}/security-groups/{security_group_id}/",  # PUT
    
}

DATASET_ENDPOINTS = {
    "create_dataset": "/teams/{team_id}/projects/{project_id}/datasets/",
    "dataset_id_path": "/teams/{team_id}/projects/{project_id}/datasets/{dataset_id}/",
}

SFS_ENDPIONTS = {
    "create_sfs": "/teams/{team_id}/projects/{project_id}/distributed_jobs/sfs/",
    "sfs_id_path": "/teams/{team_id}/projects/{project_id}/distributed_jobs/sfs/{sfs_id}/",
}

PFS_ENDPOINTS = {}

SECURITY_GROUP_ENDPOINTS = {
    "list_security_groups": "/teams/{team_id}/projects/{project_id}/security_groups/",  # GET
}

SSH_KEY_ENDPOINTS = {
    "list_ssh_keys": "/ssh_keys/",  # GET
}

RESERVE_IP_ENDPOINTS = {
    "create_reserved_ip": "/teams/{team_id}/projects/{project_id}/reserved_ips/",  # POST
    "reserved_ip_id_path": "/teams/{team_id}/projects/{project_id}/reserved_ips/{reserved_ip_id}/",  
}