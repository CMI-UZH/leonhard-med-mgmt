"""
@author: matteobe
"""

import time
from typing import Dict
import importlib

import pexpect

from clusty.configs.parser import ConfigsParser
from clusty.terminal.screen import Screen
from clusty.utils.string import replace_by_dict


class ClusterClient:
    """
    Implements a cluster client manager responsible for executing all the steps defined in the configuration YAML
    file.
    """

    clusters = {
        'leonhardmed': 'LeonhardMed',
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

        # Links to open
        links = list()

        # Setup the cluster and the screens
        name, alias, batch_jobs, tunnels, setup = self._configs.get_cluster_config()
        self.set_cluster(cluster=name)
        if setup:
            self._cluster.setup()
        cluster_screen = self._cluster.login(ssh_alias=alias)

        # Execute the batch jobs
        tunnels_ips = dict()
        for batch_job in batch_jobs:
            batch_screen = self._cluster.batch(screens=[cluster_screen,
                                                        self._configs.get_batch_job_screen_name(batch_job)],
                                               **self._configs.get_batch_job_specs(batch_job))
            screens = [cluster_screen, batch_screen]

            # Read the IP address
            batch_job_ip_address = self._cluster.ip_address(screens=screens)
            tunnels_ips[batch_job] = batch_job_ip_address

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
                    url_local = self._cluster.launch_jupyter(screens=screens,
                                                             **self._configs.get_jupyter_configs(batch_job))
                    links.append(url_local)
                else:
                    self._cluster.run(screens=screens, commands=cmd)

        # Create the tunnels
        tunnels = replace_by_dict(values=tunnels, replace=tunnels_ips)
        for idx, tunnel in enumerate(tunnels):
            name = "tunnel" if idx == 0 else f"tunnel{idx}"
            self._cluster.login(ssh_alias=alias, binding=tunnel, name=name)

        # Open links in the default browser
        # TODO: Optimize link opening
        for link in links:
            terminal = pexpect.spawn(f"open {link}")
            time.sleep(0.2)
            terminal.close(force=True)

    # TODO: Test feature to make sure it behaves correctly
    # TODO: Problem, because screen name is not same as cluster name
    def stop(self):
        """
        Close all the screens defined in the configuration file, and as a consequence stop all the processes launched
        inside those screens.
        """

        cluster_screen_name, _, batch_jobs, _, _ = self._configs.get_cluster_config()
        cluster_screens = Screen.list(name=cluster_screen_name)

        if cluster_screens:
            cluster_screen_id, cluster_screen, _ = cluster_screens[0]
            terminal = Screen.attach(screen=cluster_screen_id)

            for batch_job in batch_jobs:
                batch_screen_name = self._configs.get_batch_job_screen_name(batch_job)
                batch_screens = Screen.list(name=batch_screen_name, terminal=terminal)

                for _, batch_screen, _ in batch_screens:
                    Screen.kill(name=batch_screen, terminal=terminal)
                    print(f"Quit screen '{batch_screen}' inside screen '{cluster_screen}'.")

            Screen.detach(terminal)

        for cluster_screen_id, cluster_screen, _ in cluster_screens:
            Screen.kill(cluster_screen_id)
            print(f"Quit screen '{cluster_screen}'.")

        tunnels = Screen.list(name="tunnel")
        for _, screen_name, _ in tunnels:
            Screen.kill(screen_name)
            print(f"Quit screen '{screen_name}'.")

        if cluster_screens:
            print(f"Completed closing of all screens.")
        else:
            print(f"No screens to close are present.")
