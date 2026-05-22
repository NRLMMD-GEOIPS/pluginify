# # # This source code is subject to the license referenced at
# # # https://github.com/NRLMMD-GEOIPS.

"""TestPluginRegistry Class used for Unit Testing the Plugin Registries."""

from glob import glob
import logging
from os.path import basename, splitext

import pytest
import yaml
from importlib.resources import files
from pydantic import ValidationError as PydanticValidationError

from pluginify.errors import PluginError, PluginRegistryError, PluginValidationError
from pluginify.interfaces import configs
from pluginify.interfaces import data_modifiers
from pluginify.utils.validators import PluginRegistryValidator
from pluginify.pydantic_models.v1.configs import ConfigPluginModel

LOG = logging.getLogger(__name__)


class FakeInterface:
    """Dummy fake interface used to cause appropriate errors from the PluginRegistry."""

    interface_type = "fake"
    name = "fake_interface"


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
    pr_validator = PluginRegistryValidator(
        namespace="pluginify.plugin_packages", fpaths=default_fpaths
    )
    # real reg validator is responsible for testing deleting and building of registries
    # based on whether or not we want that to occur:
    # I.e. whether or not config.REBUILD_REGISTRIES is set to True or
    # False
    real_reg_validator = PluginRegistryValidator(
        namespace="pluginify.plugin_packages", fpaths=None
    )

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
        pluginify.config.REBUILD_REGISTRIES is set to True.
        """
        self.real_reg_validator.delete_registries()
        # Delete again using specific packages (won't do anything) for code coverage
        self.real_reg_validator.delete_registries(packages=["pluginify"])
        self.real_reg_validator._set_class_properties(
            force_reset=True, rebuild_registries_override=True
        )
        assert self.real_reg_validator.registered_plugins

    def test_disabled_registry_creation(self):
        """Assert that the registries are not automatically rebuilt.

        This occurs if expected registry files are missing and
        pluginify.REBUILD_REGISTRIES is set to False. A FileNotFoundError
        should be raised.
        """
        self.real_reg_validator.delete_registries()
        with pytest.raises(FileNotFoundError):
            self.real_reg_validator._set_class_properties(
                force_reset=True, rebuild_registries_override=False
            )

    def test_get_plugin_metadata(self):
        """Retrieve plugin metadata from a plugin that we know exists and is correct.

        For this test, we'll be using the data_modifiers.cuboid plugin and the
        configs.stucco plugin.
        """
        self.real_reg_validator._set_class_properties(
            force_reset=True, rebuild_registries_override=True
        )
        assert data_modifiers.get_plugin_metadata("cuboid")
        assert configs.get_plugin_metadata("stucco")

    def test_get_plugin_metadata_failing_cases(self):
        """Attempt to retrieve plugin metadata from a cases that we know should fail."""
        self.real_reg_validator._set_class_properties(
            force_reset=True, rebuild_registries_override=True
        )
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

    def test_plugin_validation_error_has_useful_message(self):
        """Test PluginValidationError summarizes pydantic errors for a bad stucco."""
        # Load the real stucco.yaml as a starting point.
        stucco_path = str(files("pluginify") / "plugins/yaml/configs/stucco.yaml")
        with open(stucco_path) as fp:
            data = yaml.safe_load(fp)

        # Mutate one field so the dict violates ConfigPluginModel.
        data["spec"]["units"] = "furlongs"

        with pytest.raises(PydanticValidationError) as pyd_exc:
            ConfigPluginModel(**data)

        # Construct PluginValidationError.
        err = PluginValidationError(
            "stucco",
            "configs",
            "pluginify",
            "/fake/path/stucco.yaml",
            pyd_exc.value
        )

        assert "stucco" in str(err)
        assert "configs" in str(err)
        assert "error(s) found" in str(err)
        assert len(str(err).splitlines()) < len(str(pyd_exc.value).splitlines())

    def test_get_yaml_plugin_raises_plugin_validation_error_on_bad_yaml(
            self, tmp_path, monkeypatch
    ):
        """Test get_yaml_plugin raises PluginValidationError on bad yaml."""
        # Initialize the real registry BEFORE patching anything.
        self.real_reg_validator._set_class_properties(
            force_reset=True, rebuild_registries_override=True
        )

        # Load real stucco.yaml and dump the mutated dict inside tmp_path
        stucco_path = str(files("pluginify") / "plugins/yaml/configs/stucco.yaml")
        with open(stucco_path) as fp:
            data = yaml.safe_load(fp)

        data["name"] = "bad_stucco"
        data["spec"]["units"] = "furlongs"
        with open(tmp_path / "bad_stucco.yaml", "w") as fp:
            yaml.safe_dump(data, fp)

        # Patch the path resolver so any resources.files(package) call inside
        #    get_yaml_plugin returns tmp_path.
        monkeypatch.setattr(
            "pluginify.plugin_registry.resources.files", lambda pkg: tmp_path
        )

        # Splice a minimal fake entry into the in-memory registry.
        registry = self.real_reg_validator.registered_plugins

        registry["yaml_based"]["configs"]["bad_stucco"] = {
            "package": "pluginify",
            "relpath": "bad_stucco.yaml",
        }

        try:
            with pytest.raises(PluginValidationError) as err:
                self.real_reg_validator.get_yaml_plugin(configs, "bad_stucco")

            assert "bad_stucco" in str(err.value)
            assert "configs" in str(err.value)
            assert "error(s) found" in str(err.value)
        finally:
            # remove "bad_stucco" from the registry.
            del registry["yaml_based"]["configs"]["bad_stucco"]

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
