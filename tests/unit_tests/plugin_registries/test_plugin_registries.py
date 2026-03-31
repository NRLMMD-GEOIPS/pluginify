# # # This source code is subject to the license referenced at
# # # https://github.com/NRLMMD-GEOIPS.

"""TestPluginRegistry Class used for Unit Testing the Plugin Registries."""

from glob import glob
from importlib import import_module, metadata
import logging
from os import environ
from os.path import basename, splitext
from pprint import pformat

import pytest
import json
import yaml

from pluginify.errors import PluginError, PluginRegistryError
from pluginify.interfaces import configs
from pluginify.interfaces import data_modifiers
from pluginify.plugin_registry import PluginRegistry

LOG = logging.getLogger(__name__)


class FakeInterface:
    """Dummy fake interface used to cause appropriate errors from the PluginRegistry."""

    interface_type = "fake"
    name = "fake_interface"


class PluginRegistryValidator(PluginRegistry):
    """Subclass of PluginRegistry which adds functionality for unit testing."""

    def __init__(self, fpaths=None):
        """Initialize TestPluginRegistry Class."""
        super().__init__("pluginify.plugin_packages", _test_registry_files=fpaths)

    def validate_plugin_types_exist(self, reg_dict, reg_path):
        """Test that all top level plugin types exist in each registry file."""
        expected_plugin_types = ["yaml_based", "class_based", "text_based"]
        for p_type in expected_plugin_types:
            if p_type not in reg_dict:
                error_str = f"Expected plugin type '{p_type}' to be in the registry but"
                error_str += f" wasn't. This was in file '{reg_path}'."
                raise PluginRegistryError(error_str)

    def validate_all_registries(self):
        """Validate all registries in the current installation.

        This should be run during testing, but not at runtime.
        Ensure we do not fail catastrophically for a single bad plugin
        at runtime, so test up front to test validity.
        """
        for reg_path in self.registry_files:
            pkg_plugins = json.load(open(reg_path, "r"))
            self.validate_registry(pkg_plugins, reg_path)

    def validate_registry(self, current_registry, fpath):
        """Test all plugins found in registered plugins for their validity."""
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

    def validate_plugin_attrs(self, plugin_type, interface, name, plugin):
        """Test non-product plugin for all required attributes."""
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

    def validate_registry_interfaces(self, current_registry):
        """Test Plugin Registry interfaces validity."""
        yaml_interfaces = []
        class_interfaces = []

        # NOTE: all <pkg>/interfaces/__init__.py files MUST
        # contain a "class_based_interfaces" list and a
        # "yaml_based_interfaces" list - this is how we
        # identify the valid interface names.
        # We must avoid actually importing the interfaces within
        # the pluginify repo - or we will end up with a circular import
        # due to BaseInterface.
        for pkg in metadata.entry_points(group="pluginify.plugin_packages"):
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


class TestPluginRegistry:
    """
    Pytest-based Unit Test for the PluginRegistry Class.

    Note: Since we are not able to initialize this class due to restrictions placed by
    Pytest, if you want to change the test files used, simply replace the location below
    with the location of your new test files.
    """

    default_fpaths = glob(
        str(__file__).replace("test_plugin_registries.py", "files/**/*.yaml"),
        recursive=True,
    )

    # pr_validator uses test registry files for most tests
    pr_validator = PluginRegistryValidator(fpaths=default_fpaths)
    # real reg validator is responsible for testing deleting and building of registries
    # based on whether or not we want that to occur:
    # I.e. whether or not os.environ["PLUGINIFY_REBUILD_REGISTRIES"] is set to True or
    # False
    real_reg_validator = PluginRegistryValidator(fpaths=None)

    # Couldn't implement this class via inheritance because PyTest Raised this error:
    # PytestCollectionWarning: cannot collect test class 'TestPluginRegistry' because
    # it has a __init__ constructor (from: test_plugin_registries.py)

    # This isn't a problem though, as we can just set it as a class attribute and move
    # forward as usual. Pytest is just picky about having __init__ in Test Classes.

    # def __init__(self, fpaths=default_fpaths):
    #     super().__init__(fpaths)

    def generate_id(fpath):
        """Generate pytest id for current test."""
        test_id = "bad"
        if "/good/" in fpath:
            test_id = "good"
        return f"{test_id}-{splitext(basename(fpath))[0]}"

    def test_registered_plugin_property(self):
        """Ensure registered_plugins is valid in its nature."""
        if hasattr(self.pr_validator, "_registered_plugins"):
            del self.pr_validator._registered_plugins
        print(self.pr_validator.registered_plugins)
        assert isinstance(self.pr_validator.registered_plugins, dict)
        assert "yaml_based" in self.pr_validator.registered_plugins
        assert "class_based" in self.pr_validator.registered_plugins
        assert "text_based" in self.pr_validator.registered_plugins
        assert self.pr_validator.registered_plugins

    def test_interface_mapping_property(self):
        """Ensure interface_mapping is valid in its nature."""
        if hasattr(self.pr_validator, "_interface_mapping"):
            del self.pr_validator._interface_mapping
        if hasattr(self.pr_validator, "_registered_plugins"):
            del self.pr_validator._registered_plugins
        print(self.pr_validator.interface_mapping)
        assert isinstance(self.pr_validator.interface_mapping, dict)
        assert "yaml_based" in self.pr_validator.interface_mapping
        assert "class_based" in self.pr_validator.interface_mapping
        assert "text_based" in self.pr_validator.interface_mapping
        assert isinstance(self.pr_validator.interface_mapping["yaml_based"], list)
        assert isinstance(self.pr_validator.interface_mapping["class_based"], list)
        assert isinstance(self.pr_validator.interface_mapping["text_based"], list)

    def test_registered_class_plugins_property(self):
        """Ensure that registered_class_plugins exist and have contents."""
        if hasattr(self.pr_validator, "_registered_plugins"):
            del self.pr_validator._registered_plugins
        print(self.pr_validator.registered_class_based_plugins)
        assert isinstance(self.pr_validator.registered_class_based_plugins, dict)
        assert len(self.pr_validator.registered_class_based_plugins)

    def test_registered_yaml_plugins_property(self):
        """Ensure that registered_yaml_plugins exist and have contents."""
        if hasattr(self.pr_validator, "_registered_plugins"):
            del self.pr_validator._registered_plugins
        print(self.pr_validator.registered_yaml_based_plugins)
        assert isinstance(self.pr_validator.registered_yaml_based_plugins, dict)
        assert len(self.pr_validator.registered_yaml_based_plugins)

    def test_automatic_registry_creation(self):
        """Assert that the registries are automatically rebuilt.

        This occurs if expected registry files are missing and
        os.environ["PLUGINIFY_REBUILD_REGISTRIES"] is set to True.
        """
        environ["PLUGINIFY_REBUILD_REGISTRIES"] = "True"
        self.real_reg_validator.delete_registries()
        # Delete again using specific packages (won't do anything) for code coverage
        self.real_reg_validator.delete_registries(packages=["pluginify"])
        self.real_reg_validator._set_class_properties(force_reset=True)
        assert self.real_reg_validator.registered_plugins

    def test_disabled_registry_creation(self):
        """Assert that the registries are not automatically rebuilt.

        This occurs if expected registry files are missing and
        os.environ["PLUGINIFY_REBUILD_REGISTRIES"] is set to False. A FileNotFoundError
        should be raised.
        """
        environ["PLUGINIFY_REBUILD_REGISTRIES"] = "False"
        self.real_reg_validator.delete_registries()
        with pytest.raises(FileNotFoundError):
            self.real_reg_validator._set_class_properties(force_reset=True)

    def test_get_plugin_metadata(self):
        """Retrieve plugin metadata from a plugin that we know exists and is correct.

        For this test, we'll be using the data_modifiers.cuboid plugin and the
        configs.stucco plugin.
        """
        environ["PLUGINIFY_REBUILD_REGISTRIES"] = "True"
        self.real_reg_validator._set_class_properties(force_reset=True)
        assert data_modifiers.get_plugin_metadata("cuboid")
        assert configs.get_plugin_metadata("stucco")

    def test_get_plugin_metadata_failing_cases(self):
        """Attempt to retrieve plugin metadata from a cases that we know should fail."""
        environ["PLUGINIFY_REBUILD_REGISTRIES"] = "True"
        self.real_reg_validator._set_class_properties(force_reset=True)
        # Caused when a plugin doesn't exist under an interface's registry
        with pytest.raises(PluginRegistryError):
            data_modifiers.get_plugin_metadata("fake_plugin")
        # Caused due to invalid argument type
        with pytest.raises(TypeError):
            data_modifiers.get_plugin_metadata(1078)

        # Caused due to the registry being unable to locate this interface of a certain
        # type
        with pytest.raises(KeyError):
            self.real_reg_validator.get_plugin_metadata(FakeInterface, "fake_plugin")

    def test_get_yaml_plugin(self):
        """Retrieve valid (existing and formatted correctly) pluginify YAML plugin(s).

        Will retrieve 'stucco' config.
        """
        config = self.real_reg_validator.get_yaml_plugin(configs, "stucco")

        assert isinstance(config, dict)
        assert config["name"] == "stucco"
        assert config["interface"] == "configs"
        assert "x" in config["spec"]["dimensions"]

    def test_get_yaml_plugin_failing_cases(self):
        """Attempt to get all plugins from an interface using cases that should fail."""
        # Reconstruct the registry in memory so we start at a clean slate
        self.real_reg_validator._set_class_properties(force_reset=True)
        # Set interfaces' rebuild_registries attr to false for the time being
        configs.rebuild_registries = False

        yam_reg = self.real_reg_validator.registered_plugins.pop("yaml_based")
        # Caused due to 'yaml_based' plugins being absent from the registry
        with pytest.raises(PluginError):
            self.real_reg_validator.get_yaml_plugin(configs, "stucco")
        # Reset the yaml_based portion of the registry back to its original value
        self.real_reg_validator.registered_plugins["yaml_based"] = yam_reg

        # Caused due to invalid argument type (rebuild_registries) should be a boolean
        with pytest.raises(TypeError):
            self.real_reg_validator.get_yaml_plugin(
                configs, "stucco", rebuild_registries=Exception
            )

        # Caused due to a missing plugin
        with pytest.raises(PluginError):
            self.real_reg_validator.get_yaml_plugin(
                configs, "fake_plugin", rebuild_registries=False
            )

        stucco_relpath = self.real_reg_validator.registered_yaml_based_plugins[
            "configs"
        ]["stucco"].pop("relpath")
        self.real_reg_validator.registered_yaml_based_plugins["configs"]["stucco"][
            "relpath"
        ] = "/some/fake/path.yaml"
        # Caused due to non existent file path
        with pytest.raises(PluginRegistryError):
            self.real_reg_validator.get_yaml_plugin(configs, "stucco")
        # Reset that relative path back to its original value
        self.real_reg_validator.registered_yaml_based_plugins["configs"]["stucco"][
            "relpath"
        ] = stucco_relpath

        fake_plugin_entry = {
            "docstring": "Fake config.",
            "family": None,
            "interface": "configs",
            "package": "pluginify",
            "plugin_type": "yaml_based",
            "relpath": "plugins/yaml/configs/stucco.yaml",
        }
        self.real_reg_validator.registered_plugins["yaml_based"]["configs"][
            "fake_plugin"
        ] = fake_plugin_entry
        # Caused due to configs plugin being found in the registry but doesn't exist
        # in the actual file specified
        with pytest.raises(PluginError):
            self.real_reg_validator.get_yaml_plugin(configs, "fake_plugin")
        # Remove the fake entry from the registry
        self.real_reg_validator.registered_plugins["yaml_based"]["configs"].pop(
            "fake_plugin"
        )

        # Reset interfaces' rebuild_registries values to True
        configs.rebuild_registries = True

    def test_get_yaml_plugins(self):
        """Retrieve valid (existing and formatted correctly) pluginify YAML plugins.

        This tests PluginRegistry.get_yaml_plugins, in this case, using the sectors
        interface.
        """
        self.real_reg_validator._set_class_properties(force_reset=True)
        assert len(self.real_reg_validator.get_yaml_plugins(configs))

    def test_get_yaml_plugins_failing_cases(self):
        """Attempt to retrieve all yaml plugins from a fake interface."""
        plugins = self.real_reg_validator.get_yaml_plugins(FakeInterface)
        assert len(plugins) == 0

    def test_get_class_plugin(self):
        """Retrieve a valid (existing and formatted correctly) class plugin.

        In this test case, we are using data_modifiers.cuboid.
        """
        self.real_reg_validator._set_class_properties(force_reset=True)
        alg = self.real_reg_validator.get_class_plugin(data_modifiers, "cuboid")
        assert alg.name == "cuboid"
        assert alg.interface == "data_modifiers"

    def test_get_class_plugin_failing_cases(self):
        """Attempt to retrieve a class plugin using cases that we know will fail."""
        # Reconstruct the registry in memory so we start at a clean slate
        self.real_reg_validator._set_class_properties(force_reset=True)
        # Set data_modifiers' rebuild_registry attr to false for the time being
        data_modifiers.rebuild_registries = False
        mod_reg = self.real_reg_validator.registered_plugins.pop("class_based")
        # Caused due to 'class_based' not being at the top level of the registry
        with pytest.raises(PluginError):
            self.real_reg_validator.get_class_plugin(data_modifiers, "cuboid")
        # Reset the registry to its original state
        self.real_reg_validator.registered_plugins["class_based"] = mod_reg

        # Caused due to invalid argument type (rebuild_registries) should be a boolean
        with pytest.raises(TypeError):
            self.real_reg_validator.get_class_plugin(
                data_modifiers, "cuboid", rebuild_registries=Exception
            )

        # Caused due to a missing plugin
        with pytest.raises(PluginError):
            self.real_reg_validator.get_class_plugin(
                data_modifiers, "fake_plugin", rebuild_registries=False
            )

        fake_plugin_entry = {
            "docstring": (
                "Data manipulation steps for standard 'cuboid' algorithm.\n"
                "Generalized algorithm to apply data manipulation steps in a standard "
                "order to apply corrections to a single channel output product."
            ),
            "family": "standard",
            "interface": "data_modifiers",
            "package": "pluginify",
            "plugin_type": "class_based",
            "signature": ("(self, data, config)"),
            "relpath": "/some/fake/path.py",
        }
        self.real_reg_validator.registered_plugins["class_based"]["data_modifiers"][
            "fake_plugin"
        ] = fake_plugin_entry
        # Caused due to algorithm plugin being present in registry it's relative path
        # does not exist
        with pytest.raises(PluginRegistryError):
            self.real_reg_validator.get_class_plugin(data_modifiers, "fake_plugin")
        # Remove the fake entry from the registry
        self.real_reg_validator.registered_plugins["class_based"]["data_modifiers"].pop(
            "fake_plugin"
        )
        # reset data_modifiers' rebuild_registries attr to true
        data_modifiers.rebuild_registries = True

    def test_get_class_plugins(self):
        """Retrieve valid (existing and formatted correctly) class plugins.

        In this case, we are retrieving all pluginify class algorithm plugins.
        """
        self.real_reg_validator._set_class_properties(force_reset=True)
        assert len(self.real_reg_validator.get_class_plugins(data_modifiers))

    def test_get_class_plugins_failing_cases(self):
        """Attempt to retrieve all class plugins from a fake interface."""
        plugins = self.real_reg_validator.get_class_plugins(FakeInterface)
        assert len(plugins) == 0

    def test_retry_get_plugin(self):
        """Test that PluginRegistry.retry_get_plugin works as expected."""
        with pytest.raises(PluginError):
            self.real_reg_validator.get_class_plugin(
                data_modifiers, "fake_plugin", rebuild_registries=True
            )

    def test_create_registries_invalid_input(self):
        """Assert ValueError is raised when invalid input is sent to create_registries.

        Where 'create_registries' comes from PluginRegistry.
        """
        # Caused due to invalid input. save_type must be one of ['json', 'yaml']
        with pytest.raises(ValueError):
            self.real_reg_validator.create_registries(save_type="log")

    def test_create_registries_with_specific_packages(self, caplog):
        """Test that create_registries works with a subset of packages provided.

        In this case, packages = ['pluginify'].
        """
        # 10 is the level of LOG.debug
        with caplog.at_level(logging.DEBUG):
            self.real_reg_validator.create_registries(packages=["pluginify"])

        debug_logs = [
            record.message
            for record in caplog.records
            if record.levelno == logging.DEBUG
        ]
        assert any(["pluginify" in message for message in debug_logs])

    def test_delete_registries_with_invalid_input(self):
        """Call delete_registries with invalid input and assert that errors are raised.

        Where the expected errors are TypeErrors or PluginRegistryErrors.
        """
        # Not a list
        with pytest.raises(TypeError):
            self.real_reg_validator.delete_registries(packages=Exception)
        # Not a list of strings
        with pytest.raises(TypeError):
            self.real_reg_validator.delete_registries(packages=[1, 2, 3, 4])
        # Not a valid package under namespace 'pluginify.plugin_packages'
        with pytest.raises(PluginRegistryError):
            self.real_reg_validator.delete_registries(packages=["some_fake_package"])

    @pytest.mark.parametrize("fpath", pr_validator.registry_files, ids=generate_id)
    def test_all_registries(self, fpath):
        """Test all available yaml registries."""
        with open(fpath, "r") as fo:
            current_registry = yaml.safe_load(fo)
        self.pr_validator.validate_registry(current_registry, fpath)
