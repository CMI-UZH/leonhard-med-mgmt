"""
Test shelling into leomed
"""

import pathlib
import yaml


def test_load_yaml_config():
    # Load the configuration file
    yaml_file = pathlib.Path(__file__).parent / 'leomed.yaml'
    with open(yaml_file) as file:
        configs = yaml.full_load(file)

    assert 'machine' in configs.keys(), "No machine key defined in the configuration YAML file"
