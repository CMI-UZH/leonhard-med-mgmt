"""
Parser of batch job configuration information
"""

from typing import Tuple, List


def parse_cluster_configs(configs: dict) -> Tuple[str, str, List[str], bool]:

    cluster = configs['cluster']
    cluster_name = cluster.get('id', 'leomed')
    ssh_alias = cluster.get('host', None)
    batch_jobs = cluster.get('batch_jobs', [])
    setup = cluster.get('setup', 'False')

    if setup.lower() == 'true' or setup.lower() == 'yes':
        setup = True
    else:
        setup = False

    return cluster_name, ssh_alias, batch_jobs, setup


def parse_batch_job_configs(configs: dict, batch_job: str) -> dict:

    batch_configs = dict()
    configs = configs['batch_jobs'][batch_job]

    batch_configs['duration'] = configs.get('duration', 24)
    batch_configs['cpu'] = configs.get('cpu', 4)
    batch_configs['memory'] = configs.get('memory', 10000)
    batch_configs['gpu'] = configs.get('gpu', 0)
    batch_configs['gpu_model'] = configs.get('gpu_model', 'GeForceGTX1080Ti')

    return batch_configs
