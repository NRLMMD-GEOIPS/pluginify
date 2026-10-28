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


def _make_product_plugin(plugin_id, source_names):
    """Build a product-style YAML plugin whose `id` is a `(source_name, name)` tuple.

    The products interface lives outside pluginify, but the factory takes the
    interface from the plugin contents and stores whatever id it is given.
    """
    plugin_contents = {
        "package": "my_package",
        "relpath": "plugins/yaml/products/my_source.yaml",
        "interface": "products",
        "family": "test",
        "name": plugin_id[1],
        "docstring": "A product plugin used for testing.",
        "source_names": source_names,
    }
    return configs._plugin_yaml_to_obj(plugin_id, plugin_contents, obj_attrs={})


class TestBaseYamlPluginStr:
    """Tests for `BaseYamlPlugin.__str__`."""

    def test_str_of_factory_built_plugin(self):
        """Verify a fully populated plugin reads as name, interface, and package."""
        plugin = _make_config_plugin()
        assert str(plugin) == "my_config (configs plugin from my_package)"

    def test_str_of_product_plugin_includes_source_name(self):
        """Verify a product plugin is prefixed with the source it was retrieved for."""
        plugin = _make_product_plugin(("abi", "Infrared"), ["abi"])
        assert str(plugin) == "abi: Infrared (products plugin from my_package)"

    def test_str_of_multi_source_product_uses_id_source(self):
        """Verify the source comes from `id`, not the first entry of `source_names`."""
        plugin = _make_product_plugin(("amsu-b", "89V"), ["amsu-a_mhs", "amsu-b"])
        assert str(plugin) == "amsu-b: 89V (products plugin from my_package)"

    def test_str_without_any_fields_falls_back_to_repr(self):
        """Verify a plugin with no name falls back to the full `__repr__`."""
        plugin = BaseYamlPlugin({"a": 1})
        assert str(plugin) == "BaseYamlPlugin({'a': 1})"
        assert str(plugin) == repr(plugin)

    @pytest.mark.parametrize(
        "class_attributes, expected_str",
        [
            ({"name": "x", "interface": "configs"}, "x (configs plugin)"),
            ({"name": "x"}, "x (NoInterface plugin)"),
            (
                {"name": "x", "package": "my_package"},
                "x (NoInterface plugin from my_package)",
            ),
        ],
    )
    def test_str_with_partial_fields(self, class_attributes, expected_str):
        """Verify a missing package is left out and a missing interface is named.

        The factory requires `package`, so these plugins are built with the same
        `type()` call the factory uses, supplying only some of the attributes.
        """
        plugin = type("ConfigsPlugin", (BaseYamlPlugin,), class_attributes)({})
        assert str(plugin) == expected_str

    @pytest.mark.parametrize("falsy_name", ["", None])
    def test_str_with_falsy_name_falls_back_to_repr(self, falsy_name):
        """Verify an empty or None name falls back to the full `__repr__`."""
        plugin = type("ConfigsPlugin", (BaseYamlPlugin,), {"name": falsy_name})({})
        assert str(plugin) == "ConfigsPlugin({})"
        assert str(plugin) == repr(plugin)

    def test_str_with_non_string_name_is_printed(self):
        """Verify a truthy non-string name is printed as-is."""
        class_attributes = {
            "name": 123,
            "interface": "configs",
            "package": "my_package",
        }
        plugin = type("ConfigsPlugin", (BaseYamlPlugin,), class_attributes)({})
        assert str(plugin) == "123 (configs plugin from my_package)"


class TestBaseYamlPluginRepr:
    """Tests pinning the existing `BaseYamlPlugin.__repr__` behavior."""

    def test_repr_is_full_contents(self):
        """Verify `__repr__` still wraps the plugin's full contents.

        The full dump is intentional, so this guards against it being shortened.
        """
        plugin = _make_config_plugin()
        assert repr(plugin) == f"ConfigsPlugin({dict(plugin)!r})"
