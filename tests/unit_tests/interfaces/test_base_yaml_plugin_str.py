# # # This source code is subject to the license referenced at
# # # https://github.com/NRLMMD-GEOIPS.

"""Tests for the `__str__` and `__repr__` methods of `BaseYamlPlugin`."""

import pytest

from pluginify.interfaces import configs
from pluginify.interfaces.base import BaseYamlPlugin


def _make_config_plugin():
    """Build a YAML plugin through the real `_plugin_yaml_to_obj` factory.

    A fresh `obj_attrs` dict is passed on purpose, since the factory's default for
    that argument is a mutable dict shared across calls.
    """
    plugin_contents = {
        "package": "my_package",
        "relpath": "plugins/yaml/configs/my_config.yaml",
        "interface": "configs",
        "family": "test",
        "name": "my_config",
        "docstring": "A config plugin used for testing.",
    }
    return configs._plugin_yaml_to_obj("my_config", plugin_contents, obj_attrs={})


class TestBaseYamlPluginStr:
    """Tests for `BaseYamlPlugin.__str__`."""

    def test_str_of_factory_built_plugin(self):
        """Verify a fully populated plugin reads as name, interface, and package."""
        plugin = _make_config_plugin()
        assert str(plugin) == "my_config (configs plugin from my_package)"

    def test_str_without_any_fields_falls_back_to_repr(self):
        """Verify a plugin with no name falls back to the full `__repr__`."""
        plugin = BaseYamlPlugin({"a": 1})
        assert str(plugin) == "BaseYamlPlugin({'a': 1})"
        assert str(plugin) == repr(plugin)

    @pytest.mark.parametrize(
        "class_attributes, expected_str",
        [
            ({"name": "x", "interface": "configs"}, "x (configs plugin)"),
            ({"name": "x"}, "x (plugin)"),
        ],
    )
    def test_str_with_partial_fields(self, class_attributes, expected_str):
        """Verify missing fields are left out of the description.

        The factory requires `package`, so these plugins are built with the same
        `type()` call the factory uses, supplying only some of the attributes.
        """
        plugin = type("ConfigsPlugin", (BaseYamlPlugin,), class_attributes)({})
        assert str(plugin) == expected_str


class TestBaseYamlPluginRepr:
    """Tests pinning the existing `BaseYamlPlugin.__repr__` behavior."""

    def test_repr_is_full_contents(self):
        """Verify `__repr__` still wraps the plugin's full contents.

        The full dump is intentional, so this guards against it being shortened.
        """
        plugin = _make_config_plugin()
        assert repr(plugin) == f"ConfigsPlugin({dict(plugin)!r})"
