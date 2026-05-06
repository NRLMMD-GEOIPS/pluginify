:orphan:

```{dropdown} Distribution Statement

| # # # This source code is subject to the license referenced at
| # # # https://github.com/NRLMMD-GEOIPS.

```

(class-based-plugins)=

# Class-Based Plugins

Class-based plugins are Python classes that extend
{class}`BaseClassPlugin <pluginify.interfaces.class_based_plugin.BaseClassPlugin>`
(or an interface-specific subclass of it). They are registered in the
`plugins/classes/` directory tree of a plugin package and are loaded via
plugin registries rather than entry points.

## Overview

A class-based plugin encapsulates its logic inside a `call()` method on the plugin
class. The plugin system wraps that call in a pre-/post-hook pipeline so that
interface-level concerns (such as converting between DataTree and array formats)
can be addressed once, in one place, rather than re-implemented in every plugin.

Class-based plugins are distinguished from legacy module-based plugins by the
`is_derived_from_module` flag stored in the plugin registry. True class-based plugins
derive from `BaseClassPlugin` (or an interface-specific base) and set this flag to
`False`. Legacy plugins that were originally plain Python modules and later converted to
objects will have `is_derived_from_module` set to `True`.

## Required class attributes

Every concrete (non-abstract) class-based plugin must define three class-level
attributes:

`interface`
: The interface type the plugin belongs to (e.g. `"data_modifiers"`,
`"algorithms"`). This is **typically inherited** from the interface-level
base class and does not need to be set on every plugin.

`family`
: The plugin family (e.g. `"standard"`). Families group plugins within an
interface that share the same expected call signature.

`name`
: The unique plugin name (e.g. `"cuboid"`). No two plugins in the same
interface may share the same name.

The base class validates these at class-definition time via
`__init_subclass__`. If any attribute is missing, non-string, or empty, a
`TypeError` or `ValueError` is raised immediately.

## The `call()` method

Every concrete plugin class must implement `call()`. This is where the plugin's
actual data processing logic lives. The signature of `call()` is automatically
mirrored onto the plugin instance's `__call__` (see {ref}`call-dispatch`), so
users invoke a plugin like a normal function.

```{warning}
`call()` should **not** accept `**kwargs`. Unconstrained keyword arguments
are reserved for the hook methods (see {ref}`hook-system`).
```

## `__call__` dispatch

When a class-based plugin is instantiated, `BaseClassPlugin.__init_subclass__`
automatically builds an `__call__` method on the subclass. The generated
`__call__` chains through the following pipeline:

1. `_invoke()`
2. `_pre_call()` — skipped if `data=None` is passed
3. `call()`
4. `_post_call()` — skipped if `data=None` is passed

The `__call__` method's signature is a mirror of `call()` (it carries the same
parameter names, annotations, and defaults). This means autocompletion and
introspection tools show the plugin's actual signature to callers.

```{important}
Plugins **must not** override `__call__`. Doing so raises a `TypeError` at
class-definition time.
```

If a caller passes `data=None` (the default), the hook methods are skipped and
`call()` is invoked directly. This is useful for plugins that do not process
external data.

(hook-system)=

## Hook system

`BaseClassPlugin` provides two hook methods that can be overridden on
interface-level base classes to add common pre- and post-processing.

### `_pre_call(self, data=None, *args, **kwargs)`

Runs **before** `call()`. The default implementation returns `data` unchanged.

Typical use: convert an incoming `xarray.DataTree` into a NumPy array so that
plugin authors can write `call()` signatures that work with arrays instead of
DataTree objects.

### `_post_call(self, data=None, *args, **kwargs)`

Runs **after** `call()`. The default implementation returns `data` unchanged.

Typical use: wrap the result of `call()` back into a DataTree (or other
package-specific container) before returning it to the caller.

```{note}
Both hooks receive the same `*args` and `**kwargs` that were passed to
`__call__()`, so they have access to all plugin arguments.
```

## Registration

To register a class-based plugin:

1. Create a `.py` file under `plugins/classes/{interface}/{plugin_name}.py`.
2. Define the plugin class (inheriting from the interface-level base class).
3. Expose the plugin by setting `PLUGIN_CLASS = YourPluginClass` at module level.
4. Run `pluginify create` (or let the automatic rebuild handle it). The command
   discovers `PLUGIN_CLASS` in each module under `plugins/classes/` and registers
   the class in the plugin registry.

The plugin registry stores information including the plugin's `relpath`,
`package`, `interface`, `family`, `name`, and a boolean `is_derived_from_module`
flag.

(interface-level-base-classes)=

## Interface-level base classes

To create a new category of class-based plugins, define two things:

### 1. An abstract base plugin class

Create a subclass of `BaseClassPlugin` and pass `abstract=True`:

```python
from pluginify.interfaces.class_based_plugin import BaseClassPlugin

class BaseGreeterPlugin(BaseClassPlugin, abstract=True):
    """Base class for greeter plugins."""
    interface = "greeters"   # optional; can be inherited by subclasses

    def _pre_call(self, data=None, *args, **kwargs):
        # transform data before call()
        return data

    def _post_call(self, data=None, *args, **kwargs):
        # transform data after call()
        return data
```

The `abstract=True` keyword tells `__init_subclass__` to skip validation.
Abstract base classes do not need to define `family`, `name`, or `call()`.

### 2. An interface class

Create a subclass of `BaseClassInterface` and assign the abstract base plugin
class to its `plugin_class` attribute:

```python
from pluginify.interfaces.base import BaseClassInterface

class GreetersInterface(BaseClassInterface):
    name = "greeters"
    plugin_class = BaseGreeterPlugin
    required_args = {"standard": ["name"]}
    required_kwargs = {"standard": []}

greeters = GreetersInterface()
```

The `plugin_class` attribute is how the system knows which base class to use
when constructing plugin objects from registry entries. Every class-based
interface **must** set this attribute.

## Interface validation

`BaseClassInterface` provides several methods to validate plugins:

`plugin_is_valid(plugin)`
: Checks that a plugin's `call()` signature matches the expected positional
arguments (`required_args`) and keyword arguments (`required_kwargs`) for
its family. Raises `PluginError` on mismatch.

`plugins_all_valid()`
: Validates every plugin under the interface. Returns `True` only if all
plugins pass.

`test_interface()`
: Runs a comprehensive test: retrieves all plugins, validates each one,
and returns a dictionary with validity status, plugin functions, families,
and docstrings.

This validation ensures that every registered plugin conforms to the call
signature expected by the code that will invoke it.

## Minimal complete example

### Interface definition

`my_package/interfaces/class_based/greeters.py`:

```python
from pluginify.interfaces.class_based_plugin import BaseClassPlugin
from pluginify.interfaces.base import BaseClassInterface

class BaseGreeterPlugin(BaseClassPlugin, abstract=True):
    """Base class for greeter plugins."""
    interface = "greeters"

class GreetersInterface(BaseClassInterface):
    name = "greeters"
    plugin_class = BaseGreeterPlugin
    required_args = {"standard": ["name"]}
    required_kwargs = {"standard": []}

greeters = GreetersInterface()
```

`my_package/interfaces/__init__.py`:

```python
from my_package.interfaces.class_based.greeters import greeters
```

### Plugin implementation

`my_package/plugins/classes/greeters/hello.py`:

```python
from my_package.interfaces.class_based.greeters import BaseGreeterPlugin

class HelloGreeterPlugin(BaseGreeterPlugin):
    """Greets with a hello message."""
    name = "hello"
    family = "standard"

    def call(self, name):
        """Return a greeting for the given name."""
        return f"Hello, {name}!"

PLUGIN_CLASS = HelloGreeterPlugin
```

After running `pluginify create`, the plugin is available as:

```python
from my_package.interfaces import greeters

plugin = greeters.get_plugin("hello")
result = plugin(name="World")
# result == "Hello, World!"
```