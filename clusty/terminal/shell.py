"""
Create a shell terminal using pexpect
"""

import pexpect


class Shell(pexpect.spawn):
    def __init__(self):
        super().__init__('sh')
