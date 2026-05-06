# # # This source code is subject to the license referenced at
# # # https://github.com/NRLMMD-GEOIPS.

"""Exceptions raised by the pluginify package.

Provides two error classes:

- ``PluginError`` — raised when an individual plugin is malformed, missing
  required attributes, or otherwise invalid.
- ``PluginRegistryError`` — raised when a plugin registry itself is missing,
  corrupt, or contains duplicate/conflicting entries across packages.
"""


class PluginError(Exception):
    """Exception raised for errors related to an individual plugin."""

    pass


class PluginRegistryError(Exception):
    """Exception raised for errors related to a plugin registry."""

    pass