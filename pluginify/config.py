"""Module containing configuration variables needed for pluginify to run."""


def _load_config_values():
    """Load and override pluginify configuration variables if they exist.

    The configuration file for this package is expected to be found at
    `~/.config/pluginify/config.yaml`. If present, load the contents of that file and
    look for 'NAMESPACE', 'REBUILD_REGISTRIES' key, value pairs. If found, override the
    current value of NAMESPACE and/or REBUILD_REGISTRIES.
    """
    # These imports are buried to avoid polling pluginify.config import namespace
    from os.path import exists
    from pathlib import Path
    from platformdirs import user_config_dir

    from yaml import safe_load

    config_path = Path(user_config_dir("pluginify")) / "config.yaml"

    NAMESPACE = "pluginify.plugin_packages"
    REBUILD_REGISTRIES = True

    if exists(config_path):
        with open(config_path, "r") as file_stream:
            config = safe_load(file_stream)

        NAMESPACE = config.get("NAMESPACE", NAMESPACE)
        REBUILD_REGISTRIES = config.get("REBUILD_REGISTRIES", REBUILD_REGISTRIES)

    return NAMESPACE, REBUILD_REGISTRIES


NAMESPACE, REBUILD_REGISTRIES = _load_config_values()
