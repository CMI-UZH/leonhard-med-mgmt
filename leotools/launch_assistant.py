#!/usr/bin/env python

import argparse
from pathlib import Path

import yaml

from leotools.cluster.client import ClusterClient


epilog_str = """
**** Example usage ****
Launch a cluster setup:
    clusty start --config /path/to/custom/config/file\n

Stop a cluster setup:
    clusty stop --config /path/to/custom/config/file\n
"""


def cluster_launch_assistant():
    """
    Cluster computing (HPC) environment launch assistant

    Takes care of launching an SSH connection to a specified cluster, creating screens to execute commands,
    launch Singularity images and Jupyter notebooks, as well as tunneling jupyter notebooks through SSH.
    """

    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, epilog=epilog_str)
    parser.add_argument('action', nargs='?', default='start', choices=['start', 'stop'])
    parser.add_argument('-c', '--config', type=str,
                        default=str((Path('.') / ".clusty.yaml").resolve()),
                        help="Specify a custom YAML configuration file to be used for the launch assistant.\n"
                             "By default the file .clusty.yaml is used (if it exists in the current directory.")

    args = parser.parse_args()

    with open(args.config) as file:
        configs = yaml.full_load(file)

    client = ClusterClient(configs=configs)

    if args.action == 'start':
        client.start()
    elif args.action == 'stop':
        client.stop()


if __name__ == "__main__":
    cluster_launch_assistant()
