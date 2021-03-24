"""
Class to login to the LeonhardMed cluster
"""

import subprocess
import getpass
from leotools.screen import ScreenHandler


class LeonhardMed:

    def __init__(self):
        self.screen = ScreenHandler()

    def login(self) -> subprocess.Popen:
        """Login to the LeonhardMed cluster and return a process"""
        screen_name = self.screen.create(name='leomed')
        screen = self.screen.attach(name=screen_name)

        cmd = f"ssh medinfmk".encode('utf-8')
        out, err = screen.communicate(cmd)

        verification_code = getpass.getpass('Verification code: ').encode('utf-8')
        screen.communicate(verification_code)

        password = getpass.getpass('ETH password: ').encode('utf-8')
        screen.communicate(password)

        return screen

