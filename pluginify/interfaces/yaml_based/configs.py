# # # This source code is subject to the license referenced at
# # # https://github.com/NRLMMD-GEOIPS.

"""Configs interface class."""

from pluginify.interfaces.base import BaseYamlInterface


class ConfigsInterface(BaseYamlInterface):
    """Configs interface class."""

    name = "configs"
    use_pydantic = True


configs = ConfigsInterface()
