# # # This source code is subject to the license referenced at
# # # https://github.com/NRLMMD-GEOIPS.

"""Data modifiers interface class.

This is a 'dummy' interface which is strictly used for testing pluginify. All plugins
of this interface are also 'dummy' plugins strictly used for testing this package.
"""

from pluginify.interfaces.class_based_plugin import BaseClassPlugin
from pluginify.interfaces.base import BaseClassInterface


class BaseDataModifierPlugin(BaseClassPlugin, abstract=True):
    """Dummy base class for data_modifier plugins."""

    pass


class DataModifiersInterface(BaseClassInterface):
    """Data Modifiers interface class.

    This is a 'dummy' interface which is strictly used for testing pluginify. All
    plugins of this interface are also 'dummy' plugins strictly used for testing this
    package.
    """

    name = "data_modifiers"
    plugin_class = BaseDataModifierPlugin

    required_args = {
        "standard": ["data", "config"],
    }

    required_kwargs: dict[str, list[str]] = {"standard": []}


data_modifiers = DataModifiersInterface()
