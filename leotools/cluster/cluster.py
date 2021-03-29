"""
Interface for clusters login
"""

from abc import ABC, abstractmethod


class Cluster(ABC):

    def __init__(self, cluster_id: str, name: str, host_address: str, ssh_alias: str = None):
        self.id = cluster_id
        self.name = name
        self.host_address = host_address
        self.ssh_alias = ssh_alias

    @abstractmethod
    def setup(self, port: int) -> None:
        """Setup SSH connection to cluster using specified port"""
        pass

    @abstractmethod
    def login(self) -> str:
        """Login to the cluster"""
        pass
