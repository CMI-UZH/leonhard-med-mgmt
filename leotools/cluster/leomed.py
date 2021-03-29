"""
Implement the LeonhardMed cluster adapter
"""

import re
import getpass
import pexpect

from leotools.terminal.screen import Screen
from leotools.terminal.ssh import config_host
from leotools.cluster.cluster import Cluster

wait_period = 0.1


class LeonhardMed(Cluster):

    def __init__(self, ssh_alias: str = "medinfmk"):
        super().__init__(cluster_id="leomed",
                         name="LeonhardMed",
                         host_address="login.medinfmk.leonhard.ethz.ch",
                         ssh_alias=ssh_alias)
        # TODO: Add binding of connection (for Jupyter batch scripts)

    def setup(self) -> None:
        """Setup procedure, responsible for adding the configuration options to connect to LeoMed in the SSH config
        file"""

        # Gather the required user input
        user = input(f"ETHZ / {self.name} username: ")
        leomed_key = input(f"{self.name} SSH key file (Press Enter for default: leomed): ")
        leomed_key = "leomed" if leomed_key == "" else leomed_key
        sciencecloud_key = input("ScienceCloud SSH key file (Press Enter for default: sciencecloud): ")
        sciencecloud_key = "sciencecloud" if sciencecloud_key == "" else sciencecloud_key
        port = int(input(f"Port to use to attach to {self.name}: "))

        # Configure the SSH hosts
        config_host(ssh_alias=self.ssh_alias, host_name=self.host_address, user=user, ssh_key=leomed_key,
                    proxy_host_name="jump.leomed.ethz.ch")
        config_host(ssh_alias="medinfmk_home", host_name=self.host_address, user=user, ssh_key=leomed_key,
                    proxy_jump="leomed_jump", forward_port=port)
        config_host(ssh_alias="leomed_jump", host_name="jump.leomed.ethz.ch", user=user, proxy_jump="sciencecloud_jump",
                    forward_port=port)
        config_host(ssh_alias="sciencecloud_jump", host_name="172.23.2.77", user=user, ssh_key=sciencecloud_key,
                    forward_port=port)

        print(f"ssh-config: setup of {self.name} completed.")

    def login(self) -> str:
        """Login to the LeonhardMed cluster"""

        # Create and attach to a screen
        screen_name = Screen.create(name=self.id)
        terminal = pexpect.spawn(f"screen -r {screen_name}")
        terminal.sendline(f"ssh {self.host_address}")

        # Login procedure
        verification_code_success = False
        password_success = False
        response = terminal.expect_exact(['Verification code', 'Welcome', pexpect.EOF, pexpect.TIMEOUT], timeout=4)
        login_success = (response == 1)
        connection_timeout = (response == 3)

        if not login_success and not connection_timeout:
            print(f"Welcome to the {self.name} login:")
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
                msg = f"Connection to {self.name} at {self.host_address} timed out."
            elif not verification_code_success:
                msg = "Incorrect verification code entered 3 times. Connection not established."
            elif not password_success:
                msg = "Incorrect password entered 3 times. Connection not established."
            raise ConnectionRefusedError(msg)
        else:
            print(f"Connected to LeonhardMed on screen: {screen_name}")

        return screen_name

    def batch(self, leomed_screen: str, batch_screen: str, cpu: int = 10, memory: int = 10000, gpu: int = 0,
              gpu_model: str = 'GeForceGTX1080Ti') -> str:
        """
        Launch a batch job on LeoMed, with certain specifics
        Requires a screen name, for a screen that is already logged in to LeoMed
        """

        if gpu == 0:
            cmd = f'bsub -Is -W 24:00 -n {cpu} -R "rusage[mem={memory}]" bash'
        else:
            cmd = f'bsub -Is -W 24:00 -n {cpu} -R "rusage[mem={memory},ngpus_excl_p=1]" -R "select[gpu_model0==' \
                  f'{gpu_model}]" bash'

        # Attach to the LeoMed screen and create a screen where to launch the batch process
        terminal = pexpect.spawn(f"screen -r {leomed_screen}")
        batch_screen = Screen.create(name=batch_screen, terminal=terminal)
        terminal.sendline(f"screen -r {batch_screen}")
        terminal.expect_list([pexpect.EOF, pexpect.TIMEOUT], timeout=wait_period)

        # Launch the batch process
        print(f"Launching batch job on {self.name} in screen '{batch_screen}'...")
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
            print(f"Batch job nr. '{job[0]}' launched on machine '{machine[0]}'")
        else:
            print(f"Could not start the batch job on {self.name}")
            Screen.quit(batch_screen, terminal)

        # Detach from the Leomed screen
        Screen.detach(terminal)
        terminal.close()

        return batch_screen
