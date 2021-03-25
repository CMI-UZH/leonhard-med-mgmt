"""
Create and attach to screens
"""

from uuid import uuid4

from leotools.terminal.shell import Shell


class Screen:
    """Create a screen class, as a entry point for static methods for dealing with screens"""

    def __init__(self):
        pass

    @staticmethod
    def create(name: str = None, unique: bool = True) -> str:
        """Create new detached screen, and duplicate"""

        name = name if name is not None else str(uuid4().hex)[0:6]

        # TODO: Check if the screen name already exists
        screen_exists = False
        if unique and screen_exists:
            name = f"{name}_{str(uuid4().hex[0:6])}"

        cmd = f"screen -d -m -S {name}".encode('utf-8')
        shell = Shell()
        _, _ = shell.communicate(input=cmd)
        shell.terminate()

        return name

    @staticmethod
    def quit(name: str) -> None:
        """Kill a screen with the given name"""

        cmd = f"screen -XS {name} quit".encode('utf-8')

        shell = Shell()
        _, _ = shell.communicate(input=cmd)
        shell.terminate()
