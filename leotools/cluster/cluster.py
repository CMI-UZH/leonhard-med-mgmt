"""
@author: matteobe
"""

import re
from abc import ABC, abstractmethod
from typing import Union, List, Tuple

import pexpect

from leotools.terminal.screen import Screen
from leotools.utils.validation import format_input_to_list


class Cluster(ABC):
    """
    Interface definition for a computing cluster, which includes the definition of the cluster identifier,
    the host address and the SSH alias used to access the cluster
    """

    def __init__(self, cluster_id: str, name: str, host_address: str, ssh_alias: str = None):
        self._id = cluster_id
        self._name = name
        self._host_address = host_address
        self._ssh_alias = ssh_alias

    @abstractmethod
    def setup(self) -> None:
        """Setup SSH connection to cluster using specified port"""
        pass

    @abstractmethod
    def login(self, ssh_alias: str = None, binding: str = None) -> str:
        """Login to the cluster"""
        pass

    @abstractmethod
    def batch(self, *args, **kwargs):
        """Start a batch job on the cluster"""
        pass

    @staticmethod
    def run(screens: List[str], commands: Union[str, List[str]]) -> None:
        """Run a list of commands inside nested screens (listed from outward to inward)"""

        commands = format_input_to_list(commands)

        terminal = Screen.attach_nested(screens=screens)
        for cmd in commands:
            terminal.sendline(cmd)
            terminal.expect_list([pexpect.EOF, pexpect.TIMEOUT], timeout=1)
        Screen.detach_nested(terminal=terminal, depth=len(screens), terminate=True)

        return None

    def launch_singularity(self, screens: List[str], image: str, home_dir: str = None,
                           bindings: Union[str, List[str]] = None, gpu: bool = False) -> None:
        """Launch a singularity image inside a screen"""

        terminal = Screen.attach_nested(screens=screens)
        cmd = f"singularity shell"
        if gpu is not False:
            cmd += " --nv"
        if home_dir is not None:
            cmd += f' -H {home_dir}'
        if bindings is not None:
            bindings = format_input_to_list(bindings)
            cmd += f" -B {','.join(bindings)}"
        cmd += f" {image}"

        terminal.sendline(cmd)
        terminal.expect_list([pexpect.EOF, pexpect.TIMEOUT], timeout=10)
        print(f"Launched singularity image on {self._name} in screen '{screens[-1]}'")

        Screen.detach_nested(terminal=terminal, depth=len(screens), terminate=True)

    def launch_jupyter(self, screens: List[str], port: int) -> Tuple[str, str]:
        """Launch a Jupyter notebook inside nested screens (listed from outward to inward)"""

        terminal = Screen.attach_nested(screens=screens)

        # Launch the jupyter notebook
        print(f"Launching jupyter notebook on {self._name} in screen '{screens[-1]}'...")
        cmd = f"jupyter notebook --no-browser --ip=$(hostname -i) --port {port}"
        terminal.sendline(cmd)
        terminal.expect_list([pexpect.EOF, pexpect.TIMEOUT], timeout=15)
        jupyter_output = terminal.before.decode()
        Screen.detach_nested(terminal=terminal, depth=len(screens), terminate=True)

        # Retrieve the IP address and port for port forwarding
        notebook_url = re.compile(r"(http?):\/\/([\w\.]+):([0-9]{2,5})\/\?token=(\w{16,64})", re.MULTILINE)
        protocol, address, port, token = notebook_url.findall(jupyter_output)[0]
        url_remote = f"{protocol}://{address}:{port}/?token={token}"
        url_local = f"{protocol}://127.0.0.1:{port}/?token={token}"
        binding = f"{port}:{address}:{port}"

        print(f"Jupyter notebook launched at: {url_remote}")
        print(f"... access it on your local machine at: {url_local}")

        return url_local, binding
