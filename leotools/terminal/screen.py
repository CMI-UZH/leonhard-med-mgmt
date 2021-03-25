"""
Create and attach to screens
"""

import re
from uuid import uuid4
from typing import List, Tuple
import pexpect

from leotools.terminal.shell import Shell


class Screen:
    """Create a screen class, as a entry point for static methods for dealing with screens"""

    def __init__(self):
        pass

    @classmethod
    def create(cls, name: str = None, unique: bool = True) -> str:
        """Create new detached screen, and duplicate"""

        name = name if name is not None else str(uuid4().hex)[0:4]

        screen_list = cls.list(name)
        if unique and len(screen_list):
            name = f"{name}_{str(uuid4().hex[0:4])}"

        cmd = f"screen -d -m -S {name}".encode('utf-8')
        shell = Shell()
        _, _ = shell.communicate(input=cmd)
        shell.terminate()

        return name

    @staticmethod
    def quit(name: str) -> None:
        """Kill a screen with the given name or identifier"""

        cmd = f"screen -XS {name} quit".encode('utf-8')
        shell = Shell()
        _, _ = shell.communicate(input=cmd)
        shell.terminate()

    @classmethod
    def quit_all(cls, name: str = None, exact_name_match: bool = True) -> None:
        """Quit all screens which match the passed-in name exactly or partially (depending on exact_name_match flag)"""

        screen_list = cls.list(name=name, exact_name_match=exact_name_match)
        for screen in screen_list:
            cls.quit(name=screen[0])

    @staticmethod
    def list(name: str = None, exact_name_match: bool = False) -> List[Tuple[str, str, bool]]:
        """Retrieve a list with the screen IDs associated with a given screen name, if None, retrieve all screen IDs"""

        screens = []
        terminal = pexpect.spawn('screen -ls')
        screen_list = terminal.read().decode()
        terminal.close()

        screen_pattern = re.compile(r"([0-9]{4,6})\.(\w+)\s+(\(Detached\)|\(Attached\))", re.MULTILINE)
        matched_screens = screen_pattern.findall(screen_list)

        # Select the screens to return
        for screen_id, screen_name, attach_status in matched_screens:

            add_screen = False
            if name is None:
                add_screen = True
            else:
                if exact_name_match and screen_name == name:
                    add_screen = True
                if not exact_name_match and name in screen_name:
                    add_screen = True

            if add_screen:
                screen = (screen_id, screen_name, True if attach_status == "(Detached)" else False)
                screens.append(screen)

        return screens
