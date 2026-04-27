"""
Pydantic model for pluginify configuration plugins.

NOTE: these plugins are not intended to be used. They are just provided as an example to
see how the plugin registry functions and for testing this package.
"""

from typing import Literal, Optional, Union

from pydantic import BaseModel, Field


class Dimensions(BaseModel):
    """Model representing the dimensions field of a configuration plugin."""

    y: Union[float, int] = Field(
        ..., description="The height of the product.", alias="height"
    )
    x: Union[float, int] = Field(
        ..., description="The width of the product.", alias="width"
    )
    z: Optional[Union[float, int]] = Field(
        None, description="The depth of the product.", alias="depth"
    )


class ConfigSpec(BaseModel):
    """Model for the spec of a configuration plugin."""

    material: str = Field(..., description="The material of the product.")
    units: Literal["inches", "centimeters", "feet", "meters", "kilometers", "miles"] = (
        Field(..., description="The units of the product.")
    )
    dimensions: Dimensions = Field(..., description="The dimensions of the product.")
    shape: str = Field(..., description="The shape of the product.")


class ConfigPluginModel(BaseModel):
    """Model for yaml configuration plugins.

    Config plugins and all fields in those plugins are 'dummy' and strictly used for
    testing purposes. For examples of real plugins which actually act upon data, see
    https://github.com/NRLMMD-GEOIPS/geoips/tree/main/geoips/plugins.
    """

    apiVersion: str = Field(
        "pluginify/v1",
        description="The api version in which the plugin was implemented under.",
    )
    interface: str = Field(
        ..., description="The interface which this plugin adheres to."
    )
    name: str = Field(..., description="The name of the plugin.")
    family: str = Field(..., description="The family of the plugin.")
    docstring: str = Field(
        ..., description="A description of the plugin and what it does."
    )
    spec: ConfigSpec = Field(..., description="Specification of the product.")
