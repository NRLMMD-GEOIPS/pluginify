# # # This source code is subject to the license referenced at
# # # https://github.com/NRLMMD-GEOIPS.

"""Configs interface class."""

from pluginify.interfaces.base import BaseYamlInterface
from pluginify.pydantic_models.v1.configs import ConfigPluginModel


class ConfigsInterface(BaseYamlInterface):
    """Configs interface class."""

    name = "configs"
    use_pydantic = True
    validator = ConfigPluginModel


configs = ConfigsInterface()
