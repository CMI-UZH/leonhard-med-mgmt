"""
Author: @matteobe
"""

from typing import Tuple, List
from pathlib import Path

import yaml

from clusty.utils.validation import validate_schema, format_input_to_list


class ConfigsParser:
    """
    Class for parsing the YAML configuration file.

    The default schema is defined in the configs folder under the schema.yaml file.
    """

    with open((Path(__file__).parent / "schema.yaml").resolve(), 'rb') as f:
        config_schema = yaml.full_load(f)

    def __init__(self, configs: dict):
        self._configs = validate_schema(document=configs, schema=ConfigsParser.config_schema)

    def get_cluster_config(self) -> Tuple[str, str, List[str], bool]:

        cluster = self._configs['cluster']
        cluster_name = cluster['id']
        ssh_alias = cluster.get('host', None)
        batch_jobs = format_input_to_list(cluster.get('batch_jobs', list()))
        setup = cluster.get('setup', False)

        return cluster_name, ssh_alias, batch_jobs, setup

    def get_batch_job_configs(self, batch_job: str) -> dict:
        return self._configs['batch_jobs'][batch_job]

    def get_batch_job_screen_name(self, batch_job: str) -> str:
        configs = self.get_batch_job_configs(batch_job)
        screen = configs.get('screen', batch_job)
        return screen

    def get_batch_job_specs(self, batch_job: str) -> dict:
        """
        Get the configuration elements of a batch job
        """
        batch_configs = dict()
        configs = self.get_batch_job_configs(batch_job)

        batch_configs['duration'] = configs['duration']
        batch_configs['cpu'] = configs['cpu']
        batch_configs['memory'] = configs['memory'] * 1000
        batch_configs['gpu'] = configs['gpu']
        batch_configs['gpu_model'] = configs['gpu_model']

        return batch_configs

    def get_batch_job_env(self, batch_job: str) -> List[str]:
        """
        Get a batch job environment declarations
        """
        configs = self.get_batch_job_configs(batch_job)
        env_vars = [f"export {env_var}" for env_var in configs.get('env', list())]
        return env_vars

    def get_batch_job_commands(self, batch_job: str) -> List[str]:
        """
        Get the commands to execute in the batch job
        """
        configs = self.get_batch_job_configs(batch_job)
        return configs.get('run', list())

    def get_singularity_configs(self, batch_job: str) -> dict:

        singularity_configs = dict()
        configs = self.get_batch_job_configs(batch_job)['singularity']
        singularity_configs['image'] = configs['image']
        singularity_configs['home_dir'] = configs['home']
        singularity_configs['bindings'] = configs.get('bindings', None)
        singularity_configs['gpu'] = configs.get('gpu')

        return singularity_configs

    def get_jupyter_configs(self, batch_job: str) -> dict:

        jupyter_configs = dict()
        configs = self.get_batch_job_configs(batch_job)['jupyter']
        jupyter_configs['port'] = configs.get('port', 8888)

        return jupyter_configs
