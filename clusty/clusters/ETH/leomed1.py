"""
Author: @matteobe
"""

import re
import getpass
import pexpect
from typing import List

from clusty.terminal.screen import Screen
from clusty.terminal.ssh import config_host
from clusty.clusters.cluster import Cluster


class LeoMed1(Cluster):
    """
    Class responsible for login procedures and batch jobs launching on the LeonhardMed 1.0 cluster at ETH Zurich
    """

    wait_period = 0.1

    def __init__(self, ssh_alias: str = "medinfmk"):
        super().__init__(cluster_id="leomed1",
                         name="Leomed1.0",
                         host_address="login.medinfmk.leonhard.ethz.ch",
                         ssh_alias=ssh_alias)

    def setup(self) -> None:
        """Setup procedure, responsible for adding the configuration options to connect to LeoMed in the SSH config
        file"""

        # Gather the required user input
        user = input(f"ETHZ / {self._name} username: ")
        leomed_key = input(f"{self._name} SSH key file (Press Enter for default: leomed): ")
        leomed_key = "leomed" if leomed_key == "" else leomed_key
        sciencecloud_key = input("ScienceCloud SSH key file (Press Enter for default: sciencecloud): ")
        sciencecloud_key = "sciencecloud" if sciencecloud_key == "" else sciencecloud_key
        port = int(input(f"Port to use to attach to {self._name}: "))

        # Configure the SSH hosts
        config_host(ssh_alias=self._ssh_alias, host_name=self._host_address, user=user, ssh_key=leomed_key,
                    proxy_host_name="jump.leomed.ethz.ch")
        config_host(ssh_alias="medinfmk_home", host_name=self._host_address, user=user, ssh_key=leomed_key,
                    proxy_jump="leomed_jump", forward_port=port)
        config_host(ssh_alias="leomed_jump", host_name="jump.leomed.ethz.ch", user=user, proxy_jump="sciencecloud_jump",
                    forward_port=port)
        config_host(ssh_alias="sciencecloud_jump", host_name="172.23.2.77", user=user, ssh_key=sciencecloud_key,
                    forward_port=port)

        print(f"ssh-config: setup of {self._name} completed.")

    def login(self, ssh_alias: str = None, binding: str = None, name: str = None) -> str:
        """Login to the LeonhardMed cluster"""

        ssh_alias = "medinfmk" if ssh_alias is None else ssh_alias

        # Create and attach to a screen
        screen_name = self._id if name is None else name
        screen_name = Screen.create(name=screen_name)
        terminal = pexpect.spawn(f"screen -r {screen_name}")
        cmd = f"ssh {ssh_alias}"
        if binding is not None:
            cmd += f" -L {binding}"
        terminal.sendline(cmd)

        # Login procedure
        verification_code_success = False
        password_success = False
        response = terminal.expect_exact(['Verification code', 'Welcome', pexpect.EOF, pexpect.TIMEOUT], timeout=10)
        login_success = (response == 1)
        connection_timeout = (response == 3)

        if not login_success and not connection_timeout:
            print(f"Welcome to the {self._name} login:")
            # Verification code
            i = 0
            while i < 3 and not verification_code_success:
                verification_code = getpass.getpass('Verification code: ')
                terminal.sendline(verification_code)
                response = terminal.expect_exact(['password', 'Verification code', 'Permission denied'])
                verification_code_success = (response == 0)
                i += 1

            # Password
            i = 0
            while i < 3 and not password_success and verification_code_success:
                password = getpass.getpass('ETHZ password: ')
                terminal.sendline(password)
                response = terminal.expect_exact(['Welcome', 'password', 'Permission denied'])
                password_success = (response == 0)
                i += 1

        # Detach from screen and close the terminal
        Screen.detach(terminal)
        terminal.close()

        # If error in connection, kill screen and print error
        if (not login_success and (not verification_code_success or not password_success)) or connection_timeout:

            Screen.quit(screen_name)
            msg = ""
            if connection_timeout:
                msg = f"Connection to {self._name} at {ssh_alias} timed out."
            elif not verification_code_success:
                msg = "Incorrect verification code entered 3 times. Connection not established."
            elif not password_success:
                msg = "Incorrect password entered 3 times. Connection not established."
            raise ConnectionRefusedError(msg)
        else:
            print(f"Connected to LeonhardMed on screen: {screen_name}")

        return screen_name

    def batch(self, screens: List[str], duration: int = 24, cpu: int = 10, memory: int = 10000, gpu: int = 0,
              gpu_model: str = 'GeForceGTX1080Ti') -> str:
        """
        Launch a batch job on LeoMed, with certain specifics
        Requires a screen name, for a screen that is already logged in to LeoMed
        """

        if gpu == 0:
            cmd = f'bsub -Is -W {duration}:00 -n {cpu} -R "rusage[mem={memory}]" bash'
        else:
            cmd = f'bsub -Is -W {duration}:00 -n {cpu} -R "rusage[mem={memory},ngpus_excl_p=1]" '\
                  f'-R "select[gpu_model0=={gpu_model}]" bash'

        # Attach to the LeoMed screen and create a screen where to launch the batch process
        terminal = Screen.attach_nested(screens=screens[:-1])
        batch_screen = Screen.create(name=screens[-1], terminal=terminal)
        terminal.sendline(f"screen -r {batch_screen}")
        terminal.expect_list([pexpect.EOF, pexpect.TIMEOUT], timeout=LeonhardMed.wait_period)

        # Launch the batch process
        print(f"Launching batch job on {self._name} in screen '{batch_screen}'...")
        terminal.sendline(cmd)
        terminal.expect_list([pexpect.EOF, pexpect.TIMEOUT], timeout=30)
        batch_output = terminal.before.decode()

        job_pattern = re.compile(r"Job <([0-9]{3,5})> is submitted to queue", re.MULTILINE)
        machine_pattern = re.compile(r"<<Starting on ([-\w]+)>>", re.MULTILINE)
        job = job_pattern.findall(batch_output)
        machine = machine_pattern.findall(batch_output)

        # Detach from the batch screen
        Screen.detach(terminal, level=2)
        if len(job) == 1:
            print(f"... batch job nr. '{job[0]}' launched on machine '{machine[0]}'")
        else:
            print(f"... could not start the batch job on {self._name}")
            Screen.quit(batch_screen, terminal)

        # Detach from the Leomed screen
        Screen.detach(terminal)
        terminal.close()

        return batch_screen
