"""Module containing configuration variables needed for pluginify to run."""


def _get_env_name():
    """Determine the name of the environment that this code is being executed under.

    Returns
    -------
    env_name: str
        The name of the environment which was active when this code was ran. If running
        under the base environment, return 'base_env'.
    """
    # imports buried to avoid polluting this module's import namespace
    from os import environ
    from os.path import basename
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

    return env_name


def _env_to_variable(name, default):
    """Convert an environment variable (str) to a python variable (Any).

    If an environment variable under 'name' has been set, convert it to a python
    variable under a new type. Since all environment variables must be strings, we
    perform conversion so those variables can be cast into new types.

    Parameters
    ----------
    name: str
        The name of the environment variable to convert.
    default: Any
        The default value for the environment variable named 'name'..

    Returns
    -------
    converted: Any
        - The converted value of the environment variable.
    """
    # imports buried to avoid polluting this module's import namespace
    from os import getenv
    from pathlib import Path

    env_val = getenv(name)

    if env_val:

        if name == "PLUGINIFY_REGISTRY_DIRECTORY":
            return Path(env_val)
        elif name == "PLUGINIFY_REBUILD_REGISTRIES":
            return False if env_val.lower() in ["0", "false"] else True
        else:
            # PLUGINIFY_NAMESPACE
            return env_val

    return default


def _load_config_values():
    """Load and override pluginify configuration variables if they exist.

    The configuration file for this package is expected to be found at
    `~/.config/pluginify/config.yaml`. If present, load the contents of that file and
    look for 'NAMESPACE', 'REBUILD_REGISTRIES', 'REGISTRY_DIRECTORY' key, value pairs.

    For each key, value pair present, override the default value set in this function
    to what's been set in the configuration file.
    """
    # imports buried to avoid polluting this module's import namespace
    from os.path import exists
    from pathlib import Path
    from platformdirs import user_config_dir, user_cache_dir

    from yaml import safe_load

    config_path = Path(user_config_dir("pluginify")) / "config.yaml"

    NAMESPACE = "pluginify.plugin_packages"
    REBUILD_REGISTRIES = True
    REGISTRY_DIRECTORY = Path(user_cache_dir(_get_env_name()))

    # Override defaults with values set in config file if they exist
    if exists(config_path):
        with open(config_path, "r") as file_stream:
            config = safe_load(file_stream)

        NAMESPACE = config.get("NAMESPACE", NAMESPACE)
        REBUILD_REGISTRIES = config.get("REBUILD_REGISTRIES", REBUILD_REGISTRIES)
        REGISTRY_DIRECTORY = config.get("REGISTRY_DIRECTORY", REGISTRY_DIRECTORY)

    # Override defaults with values set as environment variables if they exist.
    # This overrides configuration variables if they've been set.
    NAMESPACE = _env_to_variable("PLUGINIFY_NAMESPACE", NAMESPACE)
    REBUILD_REGISTRIES = _env_to_variable(
        "PLUGINIFY_REBUILD_REGISTRIES", REBUILD_REGISTRIES
    )
    REGISTRY_DIRECTORY = _env_to_variable(
        "PLUGINIFY_REGISTRY_DIRECTORY", REGISTRY_DIRECTORY
    )

    return NAMESPACE, REBUILD_REGISTRIES, REGISTRY_DIRECTORY


NAMESPACE, REBUILD_REGISTRIES, REGISTRY_DIRECTORY = _load_config_values()


def get_registry_cache_dir(namespace, package):
    """Return the path to the parent directory of where to write registry files to.

    Where the path is formatted '~/.cache/{env_name}/{namespace}/{package}'.

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
    return REGISTRY_DIRECTORY / namespace / package
