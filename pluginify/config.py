"""Module containing configuration variables needed for pluginify to run."""


def get_registry_cache_dir(namespace, package):
    """Return the path to the parent directory of where to write registry files to.

    Where the path is formatted '~/.cache/{env_name}/{namespace}'.

    Parameters
    ----------
    namespace: str
        Namespace that your plugin packages fall under. The argument parser defaults
        this value to 'pluginify.plugin_packages', but a user can create separate
        namespaces if developing interfaces outside of pluginify.
    package: str
        Name of a plugin package that is registered under 'namespace'.

    Returns
    -------
    cache_dir: Path
        Full path to the parent directory in which registry files should be written
        for a package under namespace.
    """
    # imports buried to avoid polluting this module's import namespace
    from os import environ
    from os.path import basename
    from pathlib import Path
    from platformdirs import user_cache_dir
    import sys

    conda_env = environ.get("CONDA_DEFAULT_ENV")
    virtual_env = environ.get("VIRTUAL_ENV")
    # Conda / Mamba
    if conda_env:
        env_name = conda_env
    # venv / virtualenv
    elif sys.prefix != getattr(sys, "base_prefix", sys.prefix):
        env_name = basename(sys.prefix)
    # virtualenv also sets this sometimes
    elif virtual_env:
        env_name = basename(virtual_env)
    else:
        env_name = "base_env"

    return Path(user_cache_dir(env_name)) / namespace / package


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
