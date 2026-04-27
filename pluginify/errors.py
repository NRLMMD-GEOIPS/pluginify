# # # This source code is subject to the license referenced at
# # # https://github.com/NRLMMD-GEOIPS.

"""Pluginify error module."""


class PluginError(Exception):
    """Exception to be raised when there is an error in a plugin."""

    pass


class PluginRegistryError(Exception):
    """Exception to be raised when there is an error in a plugin registry."""

    pass
