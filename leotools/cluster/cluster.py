"""
Interface for clusters login
"""

import re
import time
from abc import ABC, abstractmethod
from typing import Union, List

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
            terminal_output = terminal.before.decode()
            print(terminal_output)
        Screen.detach_nested(terminal=terminal, depth=len(screens), terminate=True)

        return None

    def singularity(self, screens: List[str], image: str, home_dir: str = None,
                    binding: Union[str, List[str]] = None) -> None:
        """Launch a singularity image inside a screen"""

        if binding is not None:
            binding = format_input_to_list(binding)

        terminal = Screen.attach_nested(screens=screens)
        cmd = f"singularity shell"
        if home_dir is not None:
            cmd += f" -H {home_dir}"
        if binding is not None:
            cmd += f" -B {','.join(binding)}"
        cmd += f" {image}"

        terminal.sendline(cmd)
        terminal.expect_list([pexpect.EOF, pexpect.TIMEOUT], timeout=10)
        print(f"Launched singularity image on {self.name} in screen '{screens[-1]}'")

        Screen.detach_nested(terminal=terminal, depth=len(screens), terminate=True)

    def jupyter(self, screens: List[str], port: int) -> str:
        """Launch a Jupyter notebook inside nested screens (listed from outward to inward)"""

        terminal = Screen.attach_nested(screens=screens)

        # Launch the jupyter notebook
        print(f"Launching jupyter notebook on {self.name} in screen '{screens[-1]}'...")
        cmd = f"jupyter notebook --no-browser --ip=$(hostname -i) --port {port}"
        terminal.sendline(cmd)
        # BUG: jupyter notebook doesn't start when called from pexpect-created screens, even when trying to
        #  start a notebook by manually attaching to the screen command. Might have to do with iPython and the fact
        #  that it uses pexpect itself.
        #  Error: expect matches timeout and doesn't find any output in the before property, thus throwing an error
        #  in the regular expression matching
        terminal.expect_list([pexpect.EOF, pexpect.TIMEOUT], timeout=5)
        jupyter_output = terminal.before.decode()
        print(jupyter_output)
        Screen.detach_nested(terminal=terminal, depth=len(screens), terminate=True)

        # Retrieve the IP address and port for port forwarding
        notebook_url = re.compile(r"(http?):\/\/([\w\.]+):([0-9]{2,5})\/\?token=(\w{16,64})", re.MULTILINE)
        protocol, address, port, token = notebook_url.findall(jupyter_output)[0]
        print(f"protocol: {protocol}, address: {address}, port: {port}, token: {token}")
        url_remote = f"{protocol}://{address}:{port}?token={token}"
        url_local = f"{protocol}://localhost:{port}?token={token}"
        binding = f"{port}:{address}:{port}"

        print(f"Jupyter notebook launched at: {url_remote}")
        print(f"... access it on your local machine at: {url_local}")

        # Open in your default browser
        terminal = pexpect.spawn(f"open {url_local}")
        time.sleep(0.2)
        terminal.close(force=True)

        return binding
