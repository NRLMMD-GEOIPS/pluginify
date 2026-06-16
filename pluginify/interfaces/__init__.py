# # # This source code is subject to the license referenced at
# # # https://github.com/NRLMMD-GEOIPS.

"""Initialization module for pluginify interfaces."""

from pluginify.interfaces.class_based.data_modifiers import data_modifiers
from pluginify.interfaces.yaml_based.configs import configs

class_based_interfaces = ["data_modifiers"]
yaml_based_interfaces = ["configs"]

__all__ = class_based_interfaces + yaml_based_interfaces
