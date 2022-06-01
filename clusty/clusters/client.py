"""
@author: matteobe
"""

import time
from typing import Dict
import importlib

import pexpect

from clusty.configs.parser import ConfigsParser


class ClusterClient:
    """
    Implements a cluster client manager responsible for executing all the steps defined in the configuration YAML
    file.
    """

    clusters = {
        'leomed1': 'LeoMed1',
        'leomed2': 'LeoMed2'
    }

    def __init__(self, configs: Dict):
        self._configs = ConfigsParser(configs=configs)
        self._cluster = None

    def set_cluster(self, cluster: str) -> None:
        """
        Define the cluster object to be used for executing the commands
        """
        if cluster not in ClusterClient.clusters.keys():
            raise ValueError(f"Invalid cluster name passed in.\n"
                             f"Valid cluster names: {','.join(list(ClusterClient.clusters.keys()))}")

        self._cluster = getattr(importlib.import_module(f"clusty.clusters"), ClusterClient.clusters[cluster])()

    def start(self):
        """
        Start all the steps as defined in the configuration file
        """

        # Setup the cluster and the screens
        name, alias, batch_jobs, setup = self._configs.get_cluster_config()
        self.set_cluster(cluster=name)
        if setup:
            self._cluster.setup()
        cluster_screen = self._cluster.login(ssh_alias=alias)

        # Execute the batch batch jobs
        for batch_job in batch_jobs:
            batch_screen = self._cluster.batch(screens=[cluster_screen,
                                                        self._configs.get_batch_job_screen_name(batch_job)],
                                               **self._configs.get_batch_job_specs(batch_job))
            screens = [cluster_screen, batch_screen]

            # Load environment variables
            env_vars = self._configs.get_batch_job_env(batch_job)
            if env_vars is not None:
                self._cluster.run(screens=screens, commands=env_vars)

            # Run commands list
            for cmd in self._configs.get_batch_job_commands(batch_job):
                if cmd == 'SINGULARITY':
                    self._cluster.launch_singularity(screens=screens,
                                                     **self._configs.get_singularity_configs(batch_job))
                elif cmd == 'JUPYTER':
                    url_local, binding = self._cluster.launch_jupyter(screens=screens,
                                                                      **self._configs.get_jupyter_configs(batch_job))
                    self._cluster.login(ssh_alias=alias, binding=binding, name='tunnel')

                    # Open the URL in the default browser
                    terminal = pexpect.spawn(f"open {url_local}")
                    time.sleep(0.2)
                    terminal.close(force=True)
                else:
                    self._cluster.run(screens=screens, commands=cmd)

    def stop(self):
        """
        Stop all the steps as they are defined in the configuration file
        """
        # Close all screens created during the process of launching the cluster
        # TODO: Implement the procedure to close the screens
        pass
