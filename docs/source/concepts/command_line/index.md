:orphan:

```{dropdown} Distribution Statement

| # # # This source code is subject to the license referenced at
| # # # https://github.com/NRLMMD-GEOIPS.

```

(command_line)=

# Pluginify Command Line Interface (CLI)

The CLI can be used to create and delete plugin registries for a given package
namespace, in multiple different file formats. A 'package namespace' is the entry-point
plugin group set in one or more packages' pyproject.toml. It tells Python
(via package metadata) that your package exposes plugins discoverable at runtime under
a specific namespace.

For a poetry-based pyproject.toml, that looks like this:

:::toml

[tool.poetry.plugins."<my_package>.plugin_packages"]

my_package = "my_package"

:::

To use pluginify's CLI, simply run one of the following commands.

(pluginify_create)=

## pluginify create

{ref}`pluginify create <pluginify_create>`

``pluginify create`` creates plugin registry files.
These files for can be used to locate and use plugins within your own library
You should never edit these files.

To see examples of how a package can make use of these registry files, please refer to
[GeoIPS' documentation](https://github.com/NRLMMD-GEOIPS/geoips/tree/main/docs/source).

This package defaults to the ``pluginify.plugin_packages`` namespace.
It contains all plugin packages registered under pluginify.
You may specify a different name space. You can do this by providing a ``--namespace``
flag when using the pluginify CLI or by running the following command which will
permanently change the default namespace pluginify searches in.

```
pluginify config set-namespace <your_namespace>
```

You can pass ``--packages`` to limit the plugins processed.

JSON files are output by default.
You may also output yaml files for ease of viewing by passing ``--save-type yaml``.

For example:

```
pluginify create
pluginify create --packages geoips geoips_clavrx
pluginify create --save-type yaml
pluginify create --namespace <different_namespace>
```

(pluginify_delete)=

## pluginify delete

{ref}`pluginify delete <pluginify_delete>`

``pluginify delete`` removes the plugin registry files.
If no registry files are found, nothing occurs. For example:

```
pluginify delete
pluginify delete --packages geoips geoips_clavrx
pluginify delete --namespace <different_namespace>
```

(pluginify_config)=

## pluginify config

{ref}`pluginify config <pluginify_config>`

``pluginify config`` provides a set of configuration commands which direct pluginify
where to search for plugins, where to write registry files, and whether or not pluginify
should rebuild registries by default if a requested plugin is missing from the registry
files.

``pluginify config set namespace`` instructs what namespace pluginify should search
for plugins by default.

``pluginify config set rebuild-registries`` tells pluginify whether or not it should
rebuild plugin registries by default if a requested plugin is missing from the
registry files.

``pluginify config set registry-directory`` tells pluginify where by default it should
write registry files to.

For more info about the commands mentioned above, add a ``-h`` flag to the command and
execute it.
