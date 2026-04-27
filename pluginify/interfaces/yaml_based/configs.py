# # # This source code is subject to the license referenced at
# # # https://github.com/NRLMMD-GEOIPS.

"""Configs interface class.

This is a 'dummy' interface which is strictly used for testing pluginify. All plugins of
this interface are also 'dummy' plugins strictly used for testing this package.
"""

from pluginify.interfaces.base import BaseYamlInterface
from pluginify.pydantic_models.v1.configs import ConfigPluginModel


class ConfigsInterface(BaseYamlInterface):
    """Configs interface class.

    This is a 'dummy' interface which is strictly used for testing pluginify. All
    plugins of this interface are also 'dummy' plugins strictly used for testing this
    package.

    Uses Pydantic model validation instead of JSON schema validation.
    """

    name = "configs"
    use_pydantic = True
    validator = ConfigPluginModel


configs = ConfigsInterface()