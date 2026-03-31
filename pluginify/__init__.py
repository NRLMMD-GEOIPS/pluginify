# # # This source code is subject to the license referenced at
# # # https://github.com/NRLMMD-GEOIPS.

"""Pluginify __init__ module. Currently only does versioning."""

# NOTE: _version.py is generated automatically during build/install
from ._version import __version__, __version_tuple__
from pluginify import interfaces
from pluginify import utils

__all__ = ["interfaces", "utils", "__version__", "__version_tuple__"]
