"""
Interface for clusters login
"""

import re
from abc import ABC, abstractmethod
from typing import Union, List, Tuple

import pexpect

from leotools.terminal.screen import Screen
from leotools.utils.validation import format_input_to_list


class Cluster(ABC):

    def __init__(self, cluster_id: str, name: str, host_address: str, ssh_alias: str = None):
        self.id = cluster_id
        self.name = name
        self.host_address = host_address
        self.ssh_alias = ssh_alias

    @abstractmethod
    def setup(self) -> None:
        """Setup SSH connection to cluster using specified port"""
        pass

    @abstractmethod
    def login(self, ssh_alias: str = None) -> str:
        """Login to the cluster"""
        pass

    @abstractmethod
    def batch(self, *args, **kwargs):
        """Start a batch job on the cluster"""
        pass

    @staticmethod
    def run(screens: List[str], commands: List[str]) -> None:
        """Run a list of commands inside nested screens (listed from outward to inward)"""

        terminal = Screen.attach_nested(screens=screens)
        for cmd in commands:
            terminal.sendline(cmd)
            terminal.expect_list([pexpect.EOF, pexpect.TIMEOUT], timeout=1)

        Screen.detach_nested(terminal=terminal, depth=len(screens), terminate=True)

        return None

    def singularity(self, screens: List[str], image: str, home_dir: str = None,
                    binding: Union[str, List[str]] = None) -> None:
        """Launch a singularity image inside a screen"""

        if binding is not None:
            binding = format_input_to_list(binding)

        terminal = Screen.attach_nested(screens=screens)
        cmd = f"singularity shell "
        if home_dir is not None:
            cmd += f"-H {home_dir} "
        if binding is not None:
            cmd += f"-B {','.join(binding)} "
        cmd += f"{image}"

        print(f"Launching singularity image on {self.name} in screen '{screens[:-1]}'...")
        terminal.sendline(cmd)
        terminal.expect_list([pexpect.EOF, pexpect.TIMEOUT], timeout=2)

        Screen.detach_nested(terminal=terminal, depth=len(screens), terminate=True)

    def jupyter(self, screens: List[str], port: int) -> Tuple[str, str, str, str]:
        """Launch a Jupyter notebook inside nested screens (listed from outward to inward)"""

        terminal = Screen.attach_nested(screens=screens)

        # Launch the jupyter notebook
        print(f"Launching jupyter notebook on {self.name} in screen '{screens[:-1]}'...")
        cmd = f"jupyter notebook --no-browser --ip=$(hostname -i) --port {port}"
        terminal.sendline(cmd)
        terminal.expect_list([pexpect.EOF, pexpect.TIMEOUT], timeout=5)
        jupyter_output = terminal.before.decode()

        # Retrieve the IP address and port for port forwarding
        notebook_url = re.compile(r"\[I [0-9:\.]{12} \w+\] (https?):\/\/([\w\.]+):([0-9]{2,5})\/\?token=(\w{16,64})",
                                  re.MULTILINE)
        protocol, address, port, token = notebook_url.search(jupyter_output)[0]

        Screen.detach_nested(terminal=terminal, depth=len(screens), terminate=True)
        print(f"Jupyter notebook launched at: {protocol}://{address}:{port}?token={token}")

        return protocol, address, port, token
