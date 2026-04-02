"""Module containing configuration variables needed for pluginify to run."""


def _configure_namespace():
    """Override the value of NAMESPACE if found in an applicable config file.

    The configuration file for this package is expected to be found at
    `~/.config/pluginify/config.yaml`. If present, load the contents of that file and
    look for a 'NAMESPACE' key, value pair. If found, override the current value of
    NAMESPACE.
    """
    # These imports are buried to avoid polling pluginify.config import namespace
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
