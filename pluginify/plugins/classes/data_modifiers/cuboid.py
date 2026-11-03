# # # This source code is subject to the license referenced at
# # # https://github.com/NRLMMD-GEOIPS.

"""Cuboid data modifier plugin class.

This is a 'dummy' plugin which is strictly used for testing pluginify.
"""

from pluginify.interfaces.class_based.data_modifiers import BaseDataModifierPlugin


class CuboidDataModifierPlugin(BaseDataModifierPlugin):
    """Cuboid data modifier class.

    This is a 'dummy' plugin which is strictly used for testing pluginify.
    """

    name = "cuboid"
    interface = "data_modifiers"
    family = "standard"

    def call(self, data, config):
        """Modify the cuboid-like dataset using parameters from 'config'.

        Parameters
        ----------
        data: xarray.Dataset
            - The incoming xarray.Dataset to modify.
        config: dict
            - A dictionary representing the configuration plugin used to modify this
              dataset.

        Returns
        -------
        xarray.Dataset
            - The modified dataset based on the parameters set in 'config'.
        """
        for md_key, md_val in config["spec"].items():
            data[md_key] = md_val

        return data


PLUGIN_CLASS = CuboidDataModifierPlugin
