"""
Automated LeonhardMed pipeline for launching of Singularity images and Jupyter notebooks
"""

import yaml
from leotools.cluster.client import get_cluster_client
from leotools.configsparser import parse_cluster_configs, parse_batch_job_configs

# Load the configuration for the project
with open('tests/leomed.yaml') as file:
    configs = yaml.full_load(file)

# Define the cluster to use, set it up and login
name, alias, batch_jobs, setup = parse_cluster_configs(configs)

cluster = get_cluster_client(cluster=name)
if setup:
    cluster.setup()
cluster_screen = cluster.login(ssh_alias=alias)

# Launch batch jobs
screen_tracker = dict()
for batch_job in batch_jobs:
    batch_screen = cluster.batch(screens=[cluster_screen, batch_job],
                                 **parse_batch_job_configs(configs, batch_job))
    screen_tracker[batch_job] = [cluster_screen, batch_screen]

    # Execute commands in the batch job

    # TODO: Launch singularity in batch screen

    # Launch jupyter in batch - singularity screen
    # leomed.jupyter(screens=[leomed_screen, batch_screen], port=8100)

    # TODO: Bind the jupyter port with on another session

#Screen.quit_all(name='leomed', exact_name_match=False)
