# # # This source code is subject to the license referenced at
# # # https://github.com/NRLMMD-GEOIPS.

"""Pluginify __init__ module."""

# NOTE: _version.py is generated automatically during build/install
from ._version import __version__, __version_tuple__
from pluginify import interfaces
from pluginify import utils


def _configure_namespace():
    """Override the value of NAMESPACE if found in an applicable config file.

    The configuration file for this package is expected to be found at
    `~/.config/pluginify/config.yaml`. If present, load the contents of that file and
    look for a 'NAMESPACE' key, value pair. If found, override the current value of
    NAMESPACE.
    """
    from os.path import exists
    from pathlib import Path

    from yaml import safe_load

    config_path = Path.home() / ".config" / "pluginify" / "config.yaml"

    NAMESPACE = "pluginify.plugin_packages"

    if exists(config_path):
        with open(config_path, "r") as file_stream:
            config = safe_load(file_stream)

        NAMESPACE = config.get("NAMESPACE", NAMESPACE)

    return NAMESPACE


NAMESPACE = _configure_namespace()

__all__ = ["interfaces", "utils", "__version__", "__version_tuple__"]
