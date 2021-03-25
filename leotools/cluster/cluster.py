"""
Interface for clusters login
"""

from abc import ABC, abstractmethod


class Cluster(ABC):

    def __init__(self, ssh_address: str, port: int):
        self.id = None
        self.ssh_address = ssh_address
        self.port = port

    @abstractmethod
    def login(self) -> str:
        """Login to the cluster"""
        pass
