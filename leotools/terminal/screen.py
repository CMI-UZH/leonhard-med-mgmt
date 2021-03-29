"""
Create and attach to screens
"""

import time
import re
from uuid import uuid4
from typing import List, Tuple
import pexpect

from leotools.terminal.shell import Shell

wait_period = 0.1


class Screen:
    """Create a screen class, as a entry point for static methods for dealing with screens"""

    def __init__(self):
        pass

    @classmethod
    def create(cls, name: str = None, unique: bool = True, terminal: pexpect.spawn = None) -> str:
        """Create new detached screen, and duplicate"""

        terminal_passed_in = (terminal is not None)
        terminal = Shell() if terminal is None else terminal
        name = name if name is not None else str(uuid4().hex)[0:4]

        screen_list = cls.list(name=name, terminal=terminal)
        if unique and len(screen_list):
            name = f"{name}_{str(uuid4().hex[0:4])}"

        terminal.sendline(f"screen -dmS {name}")
        time.sleep(wait_period)

        if not terminal_passed_in:
            terminal.close(force=True)

        return name

    @staticmethod
    def quit(name: str, terminal: pexpect.spawn = None) -> None:
        """Kill a screen with the given name or identifier"""

        terminal_passed_in = (terminal is not None)
        terminal = Shell() if terminal is None else terminal
        if terminal is None:
            terminal = Shell()

        cmd = f"screen -XS {name} quit"
        terminal.sendline(cmd)
        time.sleep(wait_period)

        if not terminal_passed_in:
            terminal.close(force=True)

    @classmethod
    def quit_all(cls, name: str = None, exact_name_match: bool = True) -> None:
        """Quit all screens which match the passed-in name exactly or partially (depending on exact_name_match flag)"""

        screen_list = cls.list(name=name, exact_name_match=exact_name_match)
        for screen in screen_list:
            cls.quit(name=screen[0])

    @staticmethod
    def list(name: str = None, exact_name_match: bool = False, terminal: pexpect.spawn = None) \
            -> List[Tuple[str, str, bool]]:
        """Retrieve a list with the screen IDs associated with a given screen name, if None, retrieve all screen IDs"""

        cmd = "screen -ls" if name is None else f"screen -ls {name}"

        if terminal is None:
            terminal = pexpect.spawn(cmd)
            screen_list = terminal.read().decode()
            terminal.close()
        else:
            terminal.sendline(cmd)
            # BUG: Somehow screen -ls doesn't trigger a EOF for matching, and only matches the TIMEOUT
            #  the before property stored ALL shell output, not just the output of the screen
            #  Down-side, it takes long to match the timeout
            terminal.expect_list([pexpect.EOF, pexpect.TIMEOUT], timeout=wait_period)
            screen_list = terminal.before.decode()

        screen_pattern = re.compile(r"([0-9]{4,6})\.(\w+)\s+(\(Detached\)|\(Attached\))", re.MULTILINE)
        matched_screens = screen_pattern.findall(screen_list)

        # Select the screens to return
        screens = []
        for screen_id, screen_name, attach_status in matched_screens:
            add_screen = True
            if exact_name_match and not screen_name == name:
                add_screen = False

            if add_screen:
                screen = (screen_id, screen_name, True if attach_status == "(Detached)" else False)
                screens.append(screen)

        return screens

    @staticmethod
    def detach(terminal: pexpect.spawn, level: int = 1) -> None:
        """Implements the screen detach procedure for a terminal"""

        terminal.sendcontrol('a')
        # For nested screen, multiple Ctrl-a signals plus a final a keystroke must be send in order to detach correctly
        for _ in range(2, level):
            terminal.sendcontrol('a')
        if level > 1:
            terminal.send('a')
        terminal.sendcontrol('d')
        time.sleep(wait_period)
