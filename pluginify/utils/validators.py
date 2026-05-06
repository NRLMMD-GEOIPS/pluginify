"""Unit-testing support for validating plugin registry contents.

Provides the ``PluginRegistryValidator`` class, a subclass of ``PluginRegistry``
that adds methods to verify the structural correctness of registry files and the
plugins they contain.
"""

from importlib import metadata, import_module
import json
from pprint import pformat

import pytest

from pluginify.errors import PluginRegistryError
from pluginify.plugin_registry import PluginRegistry


class PluginRegistryValidator(PluginRegistry):
    """Subclass of ``PluginRegistry`` which adds functionality for unit testing.

    Provides methods to validate that registry files have the correct top-level
    structure, that all required plugin attributes are present, and that
    registered interfaces reference known interface names.
    """

    def __init__(self, namespace: str, fpaths: list[str] | None = None) -> None:
        """Initialize a ``PluginRegistryValidator``.

        Parameters
        ----------
        namespace : str
            The plugin-package namespace to operate on.
        fpaths : list of str, optional
            Explicit list of registry file paths to use. If ``None``, registry
            files are located automatically from the namespace.
        """
        self.namespace = namespace
        super().__init__(self.namespace, _test_registry_files=fpaths)

    def validate_plugin_types_exist(self, reg_dict: dict, reg_path: str) -> None:
        """Test that all top-level plugin types exist in each registry file.

        Parameters
        ----------
        reg_dict : dict
            The contents of a single registry file.
        reg_path : str
            The path to the registry file being validated.

        Raises
        ------
        PluginRegistryError
            If an expected plugin type is missing from the registry.
        """
        expected_plugin_types = ["yaml_based", "class_based", "text_based"]
        for p_type in expected_plugin_types:
            if p_type not in reg_dict:
                error_str = f"Expected plugin type '{p_type}' to be in the registry but"
                error_str += f" wasn't. This was in file '{reg_path}'."
                raise PluginRegistryError(error_str)

    def validate_all_registries(self) -> None:
        """Validate all registries in the current installation.

        This should be run during testing, but not at runtime.
        Ensure we do not fail catastrophically for a single bad plugin
        at runtime, so test up front to test validity.
        """
        for reg_path in self.registry_files:
            pkg_plugins = json.load(open(reg_path, "r"))
            self.validate_registry(pkg_plugins, reg_path)

    def validate_registry(self, current_registry: dict, fpath: str) -> None:
        """Test all plugins found in registered plugins for their validity.

        Parameters
        ----------
        current_registry : dict
            The contents of a single registry file.
        fpath : str
            The path to the registry file being validated.
        """
        try:
            self.validate_plugin_types_exist(current_registry, fpath)
        except PluginRegistryError as e:
            # xfail if this is a test, otherwise just raise PluginRegistryError
            if self._is_test:
                pytest.xfail(str(e))
            else:
                raise PluginRegistryError(e)
        try:
            self.validate_registry_interfaces(current_registry)
        except PluginRegistryError as e:
            # xfail if this is a test, otherwise just raise PluginRegistryError
            if self._is_test:
                pytest.xfail(str(e))
            else:
                raise PluginRegistryError(e)
        for plugin_type in current_registry:
            for interface in current_registry[plugin_type]:
                for plugin in current_registry[plugin_type][interface]:
                    try:
                        if interface == "products":
                            for subplg in current_registry[plugin_type][interface][
                                plugin
                            ]:
                                self.validate_plugin_attrs(
                                    plugin_type,
                                    interface,
                                    (plugin, subplg),
                                    current_registry[plugin_type][interface][plugin][
                                        subplg
                                    ],
                                )
                        elif plugin_type != "text_based":
                            self.validate_plugin_attrs(
                                plugin_type,
                                interface,
                                plugin,
                                current_registry[plugin_type][interface][plugin],
                            )
                    except PluginRegistryError as e:
                        # xfail if this is a test,
                        # otherwise just raise PluginRegistryError
                        if self._is_test:
                            pytest.xfail(str(e))
                        else:
                            raise PluginRegistryError(e)

    def validate_plugin_attrs(
        self, plugin_type: str, interface: str, name: str | tuple[str, str], plugin: dict
    ) -> None:
        """Test a plugin for all required attributes.

        Parameters
        ----------
        plugin_type : str
            The plugin type (``"yaml_based"``, ``"class_based"``).
        interface : str
            The interface name (e.g. ``"configs"``, ``"products"``).
        name : str or tuple of str
            The plugin name. For product plugins this is a ``(source, name)``
            tuple.
        plugin : dict
            The plugin metadata dictionary from the registry.

        Raises
        ------
        PluginRegistryError
            If the plugin is missing one or more required attributes.
        """
        missing = []
        if plugin_type == "yaml_based" and interface != "products":
            attrs = [
                "docstring",
                "family",
                "interface",
                "package",
                "plugin_type",
                "relpath",
            ]
        elif plugin_type == "yaml_based":
            attrs = [
                "docstring",
                "family",
                "interface",
                "package",
                "plugin_type",
                "product_defaults",
                "source_names",
                "relpath",
            ]
        else:
            attrs = [
                "docstring",
                "family",
                "interface",
                "package",
                "plugin_type",
                "signature",
                "relpath",
            ]
        for attr in attrs:
            try:
                plugin[attr]
            except KeyError:
                missing.append(attr)
        if missing:
            raise PluginRegistryError(
                f"Plugin '{name}' is missing the following required "
                f"top-level properties: '{missing}'"
            )

    def validate_registry_interfaces(self, current_registry: dict) -> None:
        """Validate that registry interfaces reference known interface names.

        Parameters
        ----------
        current_registry : dict
            The contents of a single registry file.

        Raises
        ------
        PluginRegistryError
            If one or more interfaces in the registry do not match a known
            interface name from any installed package's ``interfaces/__init__.py``.
        """
        yaml_interfaces = []
        class_interfaces = []

        # NOTE: all <pkg>/interfaces/__init__.py files MUST
        # contain a "class_based_interfaces" list and a
        # "yaml_based_interfaces" list - this is how we
        # identify the valid interface names.
        # We must avoid actually importing the interfaces within
        # the pluginify repo - or we will end up with a circular import
        # due to BaseInterface.
        for pkg in metadata.entry_points(group=self.namespace):
            try:
                mod = import_module(f"{pkg.value}.interfaces")
            except ModuleNotFoundError as resp:
                if f"No module named '{pkg.value}.interfaces'" in str(resp):
                    continue
                else:
                    raise ModuleNotFoundError(resp)
            class_interfaces += mod.class_based_interfaces
            yaml_interfaces += mod.yaml_based_interfaces

        bad_interfaces = []
        for plugin_type in ["class_based", "yaml_based"]:
            for interface in current_registry[plugin_type]:
                if (
                    interface not in class_interfaces
                    and interface not in yaml_interfaces
                ):
                    error_str = f"\nPlugin type '{plugin_type}' does not allow "
                    error_str += f"interface '{interface}'.\n"
                    error_str += "\nValid interfaces: "
                    if plugin_type == "class_based":
                        interface_list = class_interfaces
                    else:
                        interface_list = yaml_interfaces
                    error_str += f"\n{interface_list}\n"
                    error_str += "\nPlease update the following plugins "
                    error_str += "to use a valid interface:\n"
                    error_str += pformat(current_registry[plugin_type][interface])
                    bad_interfaces.append(error_str)
        if bad_interfaces:
            error_str = "The following interfaces were not valid:\n"
            for error in bad_interfaces:
                error_str += error
            raise PluginRegistryError(error_str)