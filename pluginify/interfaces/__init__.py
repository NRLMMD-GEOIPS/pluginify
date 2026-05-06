"""Interface discovery and initialization module for pluginify.

Imports all available class-based and YAML-based interface instances so that
other parts of the pluginify ecosystem can discover them via
``from pluginify.interfaces import <interface_name>``.

The ``class_based_interfaces`` and ``yaml_based_interfaces`` lists are used by
``PluginRegistryValidator.validate_registry_interfaces`` to validate that
registry entries reference known interface names.
"""

from pluginify.interfaces.class_based.data_modifiers import data_modifiers
from pluginify.interfaces.yaml_based.configs import configs

class_based_interfaces = ["data_modifiers"]
yaml_based_interfaces = ["configs"]

__all__ = class_based_interfaces + yaml_based_interfaces