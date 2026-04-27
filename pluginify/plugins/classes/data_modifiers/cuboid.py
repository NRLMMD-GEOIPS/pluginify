"""Cuboid data modifier plugin class.

This is a 'dummy' plugin which is strictly used for testing pluginify.
"""

from typing import Any

from pluginify.interfaces.class_based.data_modifiers import BaseDataModifierPlugin


class CuboidDataModifierPlugin(BaseDataModifierPlugin):
    """Cuboid data modifier class.

    This is a 'dummy' plugin which is strictly used for testing pluginify.
    """

    name = "cuboid"
    interface = "data_modifiers"
    family = "standard"

    def call(self, data: Any, config: dict) -> Any:
        """Modify the cuboid-like dataset using parameters from 'config'.

        Parameters
        ----------
        data : Any
            The incoming dataset to modify.
        config : dict
            A dictionary representing the configuration plugin used to modify this
            dataset.

        Returns
        -------
        Any
            The modified dataset based on the parameters set in 'config'.
        """
        for md_key, md_val in config["spec"].items():
            data[md_key] = md_val

        return data


PLUGIN_CLASS = CuboidDataModifierPlugin
