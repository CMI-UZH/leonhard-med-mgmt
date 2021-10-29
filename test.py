"""
Automated LeonhardMed pipeline for launching of Singularity images and Jupyter notebooks
"""

import yaml
from leotools.cluster.client import get_cluster_client
from leotools.parser import ConfigsParser

# Load the configuration for the project
with open('tests/leomed.yaml') as file:
    configs = yaml.full_load(file)
configs = ConfigsParser(configs=configs)

# Define the cluster to use, set it up and login
name, alias, batch_jobs, setup = configs.cluster()
cluster = get_cluster_client(cluster=name)
if setup:
    cluster.setup()
cluster_screen = cluster.login(ssh_alias=alias)

# Execute batch jobs
for batch_job in batch_jobs:
    # Open the screen
    batch_screen = cluster.batch(screens=[cluster_screen, configs.batch_job_screen(batch_job)],
                                 **configs.batch_job_specs(batch_job))
    screens = [cluster_screen, batch_screen]

    # Load environment variables
    env_vars = configs.batch_job_env(batch_job)
    if env_vars is not None:
        cluster.run(screens=screens, commands=env_vars)

    # Run commands list
    for cmd in configs.batch_job_commands(batch_job):
        print("cmd: ", cmd)
        if cmd == 'SINGULARITY':
            cluster.singularity(screens=screens, **configs.singularity(batch_job))
        elif cmd == 'JUPYTER':
            binding = cluster.jupyter(screens=screens, **configs.jupyter(batch_job))
            cluster.login(ssh_alias=alias, binding=binding)
        else:
            cluster.run(screens=screens, commands=cmd)
# from leotools.terminal.screen import Screen; Screen.quit_all(name='leomed', exact_name_match=False)
