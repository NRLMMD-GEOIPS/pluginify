# # # This source code is subject to the license referenced at
# # # https://github.com/NRLMMD-GEOIPS.

"""Unit test module for pluginify's config.py module."""

from pathlib import Path
from platformdirs import user_cache_dir

import pytest

from pluginify import config

env_mapping = {
    "PLUGINIFY_REBUILD_REGISTRIES": True,
    "PLUGINIFY_REGISTRY_DIRECTORY": Path(user_cache_dir(config._get_env_name())),
    "PLUGINIFY_NAMESPACE": "pluginify.plugin_packages",
}


@pytest.fixture
def mock_dirs(monkeypatch, tmp_path):
    """Mock platformdirs paths."""
    config_dir = tmp_path / "config"
    cache_dir = tmp_path / "cache"

    config_dir.mkdir()
    cache_dir.mkdir()

    # appname is the first argument of the following functions
    monkeypatch.setattr(
        "platformdirs.user_config_dir",
        lambda appname: str(config_dir),
    )
    monkeypatch.setattr(
        "platformdirs.user_cache_dir",
        lambda appname=None: str(cache_dir),
    )

    return config_dir, cache_dir


@pytest.fixture
def mock_env_name(monkeypatch):
    """Mock _get_env_name."""
    monkeypatch.setattr("pluginify.config._get_env_name", lambda: "test_env")


@pytest.mark.parametrize(
    argnames=["name", "default"],
    argvalues=[[key, val] for key, val in env_mapping.items()],
    ids=[f"{key}--{str(val)}" for key, val in env_mapping.items()],
)
def test_env_to_variable(monkeypatch, name, default):
    """Test pluginify.config:_env_to_variable method.

    Parameters
    ----------
    name: str
        The name of the environment variable.
    default: Any
        The default value of the environment variable if it doesn't already exist.
    """
    monkeypatch.delenv(name, raising=False)

    assert config._env_to_variable(name, default) == default

    monkeypatch.setenv(name, str(default))

    assert config._env_to_variable(name, default) == default


@pytest.mark.parametrize(
    argnames=["namespace", "package"],
    argvalues=[
        ["pluginify.plugin_packages", pkg] for pkg in ["pkg1", "pkg2", "pluginify"]
    ],
    ids=[f"REGISTRY_DIR--{pkg}" for pkg in ["pkg1", "pkg2", "pluginify"]],
)
def test_get_registry_cache_dir(namespace, package):
    """Test pluginify.config:get_registry_cache_dir method.

    Parameters
    ----------
    namespace: str
        The namespace which 'package' is registered under.
    package: str
        The name of the package registered to 'namespace'.
    """
    orig_reg_dir = config.REGISTRY_DIRECTORY
    config.REGISTRY_DIRECTORY = Path("/path/to/some/dir")

    assert (
        config.get_registry_cache_dir(namespace, package)
        == Path("/path/to/some/dir") / namespace / package
    )

    config.REGISTRY_DIRECTORY = orig_reg_dir

    assert (
        config.get_registry_cache_dir(namespace, package)
        == Path(orig_reg_dir) / namespace / package
    )


# All fixtures are needed so we can ensure no true defaults are overridden
def test_defaults_no_config_no_env(monkeypatch, mock_dirs, mock_env_name):
    """Ensure defaults are returned when no config or env vars exist."""
    monkeypatch.delenv("PLUGINIFY_NAMESPACE", raising=False)
    monkeypatch.delenv("PLUGINIFY_REBUILD_REGISTRIES", raising=False)
    monkeypatch.delenv("PLUGINIFY_REGISTRY_DIRECTORY", raising=False)

    namespace, rebuild, registry_dir = config._load_config_values()

    assert namespace == "pluginify.plugin_packages"
    assert rebuild is True
    assert isinstance(registry_dir, Path)


# All fixtures are needed so we can ensure no true defaults are overridden
def test_config_overrides_defaults(monkeypatch, mock_dirs, mock_env_name):
    """Ensure config file overrides defaults."""
    config_dir, _ = mock_dirs

    config_file = config_dir / "config.yaml"
    config_file.write_text("""
        NAMESPACE: pluginify.plugin_packages
        REBUILD_REGISTRIES: false
        REGISTRY_DIRECTORY: /tmp/.cache
        """)

    namespace, rebuild, registry_dir = config._load_config_values()

    assert namespace == "pluginify.plugin_packages"
    assert rebuild is False
    assert registry_dir == Path("/tmp/.cache")  # nosec B108


# All fixtures are needed so we can ensure no true defaults are overridden
def test_env_overrides_config(monkeypatch, mock_dirs, mock_env_name):
    """Ensure environment variables override config values."""
    config_dir, _ = mock_dirs

    config_file = config_dir / "config.yaml"
    config_file.write_text("""
        NAMESPACE: pluginify.plugin_packages
        REBUILD_REGISTRIES: false
        REGISTRY_DIRECTORY: /tmp/.cache
        """)

    monkeypatch.setenv("PLUGINIFY_NAMESPACE", "env.namespace")
    monkeypatch.setenv("PLUGINIFY_REBUILD_REGISTRIES", "true")
    monkeypatch.setenv("PLUGINIFY_REGISTRY_DIRECTORY", "/env/.cache")

    namespace, rebuild, registry_dir = config._load_config_values()

    assert namespace == "env.namespace"
    assert rebuild is True
    assert registry_dir == Path("/env/.cache")
