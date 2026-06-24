:orphan:

```{dropdown} Distribution Statement

| # # # This source code is subject to the license referenced at
| # # # https://github.com/NRLMMD-GEOIPS.

```

(using-plugin-registries)=

# Using Plugin Registries

Plugin registries are a cache used by plugin-based packages to speed up start up times.
By default plugin packages should automate the creation of the plugin registry.

Automatic creation of the plugin registry occurs if a requested plugin could not be
found in the registry. Pluginify will attempt to build the registry once if this failure
occurs. However, if the missing plugin persists after the registry has been
automatically created, an error will be raised informing the user how to fix this
problem.

If using manual plugin registry creation, please follow the sections
below.

## Turning Off Automatic Creation of Plugin Registries

By default, pluginify automates the creation of plugin registries. If manual creation is
preferred, all the user has to do execute the following command:

``pluginify config set rebuild-registries False``

Additionally, if you want to change the default namespace which pluginify will create
registry files for, you can execute the following command.

``pluginify config set namespace <your_namespace>``

You can also change the default location where pluginify writes registry files to
by executing the following command.

``pluginify config set registry-directory <path_to_directory>``

### Environment Variables versus Configuration Variables

Pluginify supports configuration variables and environment variables. If both are set,
environment variables will override the values of the configuration variables. All of
the configuration variables mentioned in the previous section have an equivalent
environment variable.

Adding any of the following to your your ``~/.bashrc`` or equivalent user setting file
for your machine will set a pluginify environment variable.

```
export PLUGINIFY_REBUILD_REGISTRIES='__boolean_value__'  # Replace with 'True' or 'False'
export PLUGINIFY_REGISTRY_DIRECTORY='__path_to_registry_dir__'  # Replace with a path to a certain directory
export PLUGINIFY_NAMESPACE='__namespace_name__'  # Replace with the name of your namespace
```

## When to Create/Update Plugin Registries

The plugin registries must be created/updated any time one of the following
occurs:

- A plugin package under your namespace is installed or reinstalled
- A new plugin package is installed or reinstalled
- A plugin package is uninstalled
- An individual plugin is added, edited, or removed

## How to Create/Update the Plugin Registries

``pluginify create`` executable can be called to create or update the
plugin registries.

This executable will create a separate registry for each installed GeoIPS
plugin package. Each registry will contain a dictionary of all available
plugins provided by that package. The registry will be written in the
top-level directory of the installed plugin package and will, by default, be
written in JSON and named ``registered_plugins.json``.

The executable can be called with the ``-s yaml`` option to specify the output
format as YAML rather than JSON. This is useful for debugging since YAML is,
arguably, easier to read than JSON. The YAML registries should be ignored by
your packages, though, because they are significantly slower to load than JSON.

```{admonition} Usage: pluginify

```{eval-rst}
.. typer:: pluginify.commandline_typer:app
    :prog: pluginify
```
```
