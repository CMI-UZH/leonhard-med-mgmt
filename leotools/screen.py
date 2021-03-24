"""
Create and attach to screens
"""

import subprocess
from uuid import uuid4


class Shell(subprocess.Popen):
    """
    Child class of Popen, implementing a simple bash shell
    """

    def __init__(self):
        super().__init__('/bin/bash',
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         shell=True
                         )


class ScreenHandler:
    """Create a screen class, as a entry point for static methods for dealing with screens"""

    def __init__(self):
        pass

    @staticmethod
    def create(name: str = None) -> str:
        """Create new detached screen"""
        name = name if name is not None else str(uuid4().hex)[0:32]
        cmd = f"screen -d -m -S {name}".encode('utf-8')
        shell = Shell()
        _, _ = shell.communicate(input=cmd)
        shell.terminate()

        return name

    @staticmethod
    def attach(name: str) -> subprocess.Popen:
        """Attach to existing screen"""
        # TODO: Check that screen exists and if not throw an error
        cmd = f"screen -r {name}".encode('utf-8')
        shell = Shell()
        _, _ = shell.communicate(input=cmd)

        return shell
