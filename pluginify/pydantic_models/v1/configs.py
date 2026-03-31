"""
Pydantic model for pluginify configuration plugins.

NOTE: these plugins are not intended to be used. They are just provided as an example to
see how the plugin registry functions.
"""

from typing import Literal, Optional, Union

from pydantic import BaseModel, Field


class Dimensions(BaseModel):
    """Model representing the dimensions field of a configuration plugin."""

    height: Union[float, int] = Field(
        ..., description="The height of the product.", alias="y"
    )
    width: Union[float, int] = Field(
        ..., description="The width of the product.", alias="x"
    )
    depth: Optional[Union[float, int]] = Field(
        None, description="The depth of the product.", alias="z"
    )


class ConfigSpec(BaseModel):
    """Model for the spec of a configuration plugin."""

    material: str = Field(..., "The material of the product.")
    units: Literal["inches", "centimeters", "feet", "meters", "kilometers", "miles"] = (
        Field(..., description="The units of the product.")
    )
    dimensions: Dimensions = Field(..., "The dimensions of the product.")
    shape: str = Field(..., "The shape of the product.")


class ConfigPluginModel(BaseModel):
    """Model for yaml configuration plugins."""

    interface: str = Field(
        ..., description="The interface which this plugin adheres to."
    )
    name: str = Field(..., description="The name of the plugin.")
    family: str = Field(..., description="The family of the plugin.")
    docstring: str = Field(
        ..., description="A description of the plugin and what it does."
    )
    spec: ConfigSpec = Field(..., "Specification of the product.")
