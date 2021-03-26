"""
Implement the LeonhardMed cluster adapter
"""

import time
import getpass
import pexpect

from leotools.terminal.screen import Screen
from leotools.cluster.cluster import Cluster


class LeonhardMed(Cluster):

    def __init__(self, ssh_address: str):
        super().__init__(ssh_address=ssh_address)
        self.id = 'leomed'
        # TODO: Add binding of connection (for Jupyter batch scripts)

    def login(self) -> str:
        """Login to the LeonhardMed cluster"""

        # Create a screen
        screen_name = Screen.create(name=self.id)

        # Attach to screen and launch SSH
        terminal = pexpect.spawn(f"screen -r {screen_name}")
        terminal.sendline(f"ssh {self.ssh_address}")

        # Login procedure
        verification_code_success = False
        password_success = False
        # BUG: Not matching welcome when logging in directly (not happening always)
        response = terminal.expect_exact(['Verification code', 'Welcome', pexpect.EOF, pexpect.TIMEOUT])
        login_success = (response == 1)

        if not login_success:
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
        terminal.sendcontrol('a')
        terminal.sendcontrol('d')
        terminal.close()

        # If error in connection, kill screen and print error
        if not login_success and (not verification_code_success or not password_success):
            time.sleep(1)
            Screen.quit(screen_name)
            if not verification_code_success:
                item = "verification code"
            else:
                item = "password"

            raise ConnectionRefusedError(f"Incorrect {item} entered 3 times. Connection not established.")

        else:
            print(f"Connected to LeonhardMed on screen: {screen_name}")

        return screen_name

    def batch(self, screen_name: str, cpu: int = 10, memory: int = 10000, gpu: int = 0,
              gpu_model: str = 'GeForceGTX1080Ti') -> str:

        """Launch a batch job on LeoMed, with certain specifics"""
        if gpu == 0:
            cmd = f'bsub -Is -W 24:00 -n {cpu} -R "rusage[mem={memory}]" bash'
        else:
            cmd = f'bsub -Is -W 24:00 -n {cpu} -R "rusage[mem={memory},ngpus_excl_p=1]" -R "select[gpu_model0==' \
                  f'{gpu_model}]" bash'

        # Login to leomed
        leomed_screen = self.login()

        # Attach to the screen and launch the batch job
        terminal = pexpect.spawn(f"screen -r {leomed_screen}")

        # Retrieve the screen list
        screen_list = Screen.list(name=screen_name, terminal=terminal)

        terminal.sendline(f"ssh {self.ssh_address}")


        return 'cia'
