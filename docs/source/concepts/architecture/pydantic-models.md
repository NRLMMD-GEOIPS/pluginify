:orphan:

```{dropdown} Distribution Statement

| # # # This source code is subject to the license referenced at
| # # # https://github.com/NRLMMD-GEOIPS.

```

(pydantic-models)=

# Pydantic Model Validation

Pluginify uses [Pydantic](https://docs.pydantic.dev/latest/) models to validate YAML
plugin files. This replaces the legacy JSON Schema-based validation and provides richer
error messages, automatic type coercion, and a more Pythonic API for defining validation
rules.

## Overview

When `PluginRegistry.load_plugin()` is called, it dispatches to a versioned Pydantic
model based on two fields in the plugin YAML document:

1. **`apiVersion`** — determines which package and model version to use.
2. **`interface`** — determines which model class within that version to load.

The method dynamically imports the correct Pydantic model, calls
`model_class.model_validate(data)`, and returns the resulting `model_dump()` dict. If
validation fails, Pydantic raises a `ValidationError` with details about which fields
are invalid and why.

## The `apiVersion` Field

The `apiVersion` field in a plugin YAML file follows the format:

```
"package_name/model_version"
```

For example:

```yaml
apiVersion: "pluginify/v1"
apiVersion: "my_package/v2"
```

If `apiVersion` is omitted from the YAML file, pluginify defaults to `"pluginify/v1"`.

The field is split on `"/"` to extract two components:

- **`package_name`** — the Python package that houses the Pydantic models (e.g.
  `pluginify`, `my_package`).
- **`model_version`** — the version directory under that package's `pydantic_models/`
  directory (e.g. `v1`, `v2`).

An improperly formatted `apiVersion` raises a `ValueError`.

## Directory Structure

Each package that defines Pydantic models must follow this directory layout:

```
{package}/
    pydantic_models/
        v1/
            {interface}.py
        v2/
            {interface}.py
```

Each `{interface}.py` module contains the Pydantic model classes for one version of one
interface. For example, if a package has a `configs` interface and a `sectors` interface:

```
my_package/
    pydantic_models/
        v1/
            configs.py
            sectors.py
        v2/
            configs.py
            sectors.py
```

When `load_plugin()` processes a plugin with `apiVersion: "my_package/v1"` and
`interface: sectors`, it imports `my_package.pydantic_models.v1.sectors` and looks up
the model class within that module.

## Model Naming Convention

The model class name is derived from the interface name by a deterministic transformation:

1. Singularize the interface name (e.g. ``configs`` → ``config``, ``products`` →
   ``product``).
2. Convert to title case and remove underscores (e.g. ``area_definition`` →
   ``Areadefinition``).
3. Append ``PluginModel``.

Examples:

| Interface Name     | Model Class Name        |
|--------------------|-------------------------|
| ``configs``        | ``ConfigPluginModel``   |
| ``products``       | ``ProductPluginModel``  |
| ``sectors``        | ``SectorPluginModel``   |
| ``workflows``      | ``WorkflowPluginModel`` |

``load_plugin()`` uses {py:func}`getattr` to retrieve the class by this name from the
imported module. If no matching class is found, a `ValueError` is raised.

## Model Requirements

A valid Pydantic plugin model must:

- Inherit from {py:class}`pydantic.BaseModel`.
- Include the following required fields:
  - ``apiVersion`` — API version string, defaults to ``"package_name/version"``.
  - ``interface`` — interface name string.
  - ``name`` — plugin name string.
  - ``family`` — plugin family string.
  - ``docstring`` — human-readable plugin description.
  - ``spec`` — plugin-specific specification (a nested ``BaseModel`` or model type).
- Use {py:func}`pydantic.Field` with ``description``, ``alias``, and ``...`` (ellipsis
  for required) as appropriate.

Sub-models (like the ``spec`` field) are encouraged to keep validation logic modular and
readable.

## Example: Custom Pydantic Model

Below is a minimal example of a Pydantic model for a hypothetical `my_interface`
interface:

```python
# my_package/pydantic_models/v1/my_interface.py

from pydantic import BaseModel, Field


class MyInterfaceSpec(BaseModel):
    """Model for the spec field."""

    param1: str = Field(..., description="First parameter.")
    param2: int = Field(0, description="Second parameter, defaults to 0.")


class MyInterfacePluginModel(BaseModel):
    """Model for my_interface YAML plugins."""

    apiVersion: str = Field("my_package/v1", description="API version.")
    interface: str = Field(..., description="Interface name.")
    name: str = Field(..., description="Plugin name.")
    family: str = Field(..., description="Plugin family.")
    docstring: str = Field(..., description="Plugin description.")
    spec: MyInterfaceSpec = Field(..., description="Plugin specification.")
```

With this model in place, a YAML plugin file:

```yaml
apiVersion: my_package/v1
interface: my_interface
name: example
family: standard
docstring: "An example plugin."
spec:
  param1: "hello"
```

would be validated by `model_class.model_validate(data)`. A missing required field or
incorrect type would produce a `ValidationError` listing each failure.

## How Validation Works

The full flow in `PluginRegistry.load_plugin()` is:

1. Extract `apiVersion` from the plugin data (default ``"pluginify/v1"``).
2. Split `apiVersion` into `package_name` and `model_version`.
3. Extract `interface` from the plugin data.
4. Dynamically import `{package_name}.pydantic_models.{model_version}.{interface}`.
5. Compute the model class name from the interface name.
6. Retrieve the model class via `getattr(module, model_name)`.
7. Call `model_class.model_validate(data)` to validate the plugin.

The method returns a fully validated Pydantic model instance. In `get_yaml_plugin()`,
`model_dump()` is called on the result to produce the final validated dictionary used
by the requesting interface.

## Opting Into Pydantic Validation

To use Pydantic validation for a YAML-based interface, set `use_pydantic = True` on the
interface class (a subclass of {py:class}`~pluginify.interfaces.base.BaseYamlInterface`):

```python
from pluginify.interfaces.base import BaseYamlInterface
from my_package.pydantic_models.v1.my_interface import MyInterfacePluginModel


class MyInterface(BaseYamlInterface):
    """Interface class for my_interface plugins."""

    name = "my_interface"
    use_pydantic = True
    validator = MyInterfacePluginModel
```

When `use_pydantic` is `True`, `get_yaml_plugin()` routes through
{py:meth}`~pluginify.plugin_registry.PluginRegistry.load_plugin` instead of the legacy
JSON Schema validator. Every plugin loaded by this interface will be validated using the
specified Pydantic model and its associated `apiVersion` dispatch.

.. seealso::

    - :ref:`Understanding Plugin Registries <understanding-plugin-registries>`
    - `Pydantic documentation <https://docs.pydantic.dev/latest/>`__