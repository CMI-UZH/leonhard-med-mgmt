"""
Create and attach to screens
"""

import subprocess


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
