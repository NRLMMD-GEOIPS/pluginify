# # # This source code is subject to the license referenced at
# # # https://github.com/NRLMMD-GEOIPS.

"""Data modifiers interface class."""

from pluginify.interfaces.class_based_plugin import BaseClassPlugin
from pluginify.interfaces.base import BaseClassInterface


class BaseDataModifierPlugin(BaseClassPlugin, abstract=True):
    """Base class for data_modifier plugins."""

    pass


class DataModifiersInterface(BaseClassInterface):
    """Data Modifiers interface class."""

    name = "data_modifiers"
    plugin_class = BaseDataModifierPlugin

    required_args = {
        "standard": ["data", "config"],
    }

    required_kwargs = {"standard": []}


data_modifiers = DataModifiersInterface()
