"""
Implements a clients dispatcher based on the cluster name
"""

from leotools.cluster.cluster import Cluster
from leotools.cluster.leomed import LeonhardMed

cluster_mapping = {
    'leonhardmed': LeonhardMed(),
    'leomed': LeonhardMed(),
}


def get_cluster_client(cluster: str) -> Cluster:
    """Return the correct cluster"""

    if cluster not in cluster_mapping.keys():
        raise ValueError(f"Invalid cluster name passed in.\n"
                         f"Valid cluster names: {','.join(list(cluster_mapping.keys()))}")

    return cluster_mapping[cluster]
