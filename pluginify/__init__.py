# # # This source code is subject to the license referenced at
# # # https://github.com/NRLMMD-GEOIPS.

"""Pluginify: plugin registry management for YAML and Python class plugins.

This package provides the ``PluginRegistry`` class and supporting infrastructure
for registering, retrieving, and creating plugin objects from YAML configuration
files and Python class definitions. It exposes:

- ``pluginify.interfaces`` — base classes for building custom plugin interfaces.
- ``pluginify.utils`` — utility functions (dict merging, validators).

Pluginify does not ship production plugins; it is a framework for packages that
build plugin-based infrastructure (e.g. GeoIPS).

Version information is auto-generated from git tags during build/install.
"""

# NOTE: _version.py is generated automatically during build/install
from pluginify._version import __version__, __version_tuple__
from pluginify import interfaces
from pluginify import utils

__all__ = ["interfaces", "utils", "__version__", "__version_tuple__"]