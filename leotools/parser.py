"""
Class for parsing the cluster YAML configuration file
"""

from typing import Tuple, List

from leotools.utils.validation import format_input_to_list


class ConfigsParser:

    def __init__(self, configs: dict):
        self.configs = configs

    def cluster(self) -> Tuple[str, str, List[str], bool]:

        cluster = self.configs['cluster']
        cluster_name = cluster.get('id', 'leomed')
        ssh_alias = cluster.get('host', None)
        batch_jobs = format_input_to_list(cluster.get('batch_jobs', []))
        setup = str(cluster.get('setup', 'False'))

        if setup.lower() == 'true' or setup.lower() == 'yes':
            setup = True
        else:
            setup = False

        return cluster_name, ssh_alias, batch_jobs, setup

    def __batch_configs(self, batch_job: str) -> dict:
        return self.configs['batch_jobs'][batch_job]

    def batch_job_screen(self, batch_job: str) -> str:

        configs = self.__batch_configs(batch_job)
        screen = configs.get('id', batch_job)
        return screen

    def batch_job_specs(self, batch_job: str) -> dict:

        batch_configs = dict()
        configs = self.__batch_configs(batch_job)

        batch_configs['duration'] = configs.get('duration', 24)
        batch_configs['cpu'] = configs.get('cpu', 4)
        batch_configs['memory'] = configs.get('memory', 10000)
        batch_configs['gpu'] = configs.get('gpu', 0)
        batch_configs['gpu_model'] = configs.get('gpu_model', 'GeForceGTX1080Ti')

        return batch_configs

    def batch_job_env(self, batch_job: str) -> List[str]:

        configs = self.__batch_configs(batch_job)
        env_vars = [f"export {env_var}" for env_var in configs.get('env', [])]
        return env_vars

    def batch_job_commands(self, batch_job: str) -> List[str]:

        configs = self.__batch_configs(batch_job)
        return configs.get('run', [])

    def singularity(self, batch_job: str) -> dict:

        singularity_configs = dict()
        configs = self.__batch_configs(batch_job)['singularity']
        singularity_configs['image'] = configs['image']
        singularity_configs['home_dir'] = configs.get('home', None)
        singularity_configs['binding'] = configs.get('binding', None)

        return singularity_configs

    def jupyter(self, batch_job: str) -> dict:

        jupyter_configs = dict()
        configs = self.__batch_configs(batch_job)['jupyter']
        jupyter_configs['port'] = configs.get('port', 8888)

        return jupyter_configs
