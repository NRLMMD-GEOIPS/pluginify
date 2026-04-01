:orphan:

.. dropdown:: Distribution Statement

 | # # # This source code is subject to the license referenced at
 | # # # https://github.com/NRLMMD-GEOIPS.

.. _command_line:

Pluginify Command Line Interface (CLI)
**************************************

The CLI can be used to create and delete plugin registries for a given package
namespace, in multiple different file formats. A 'package namespace' is the entry-point
plugin group set in one or more packages' pyproject.toml. It tells Python
(via package metadata) that your package exposes plugins discoverable at runtime under
a specific namespace.

For a poetry-based pyproject.toml, that looks like this:

.. code-block:: toml

    [tool.poetry.plugins."<my_package>.plugin_packages"]

    my_package = "my_package"

To use pluginify's CLI, simply run one of the following commands.

.. _pluginify_create:

pluginify create
================

:ref:`pluginify create <pluginify_create>`

``pluginify create`` creates plugin registry files.
These files for can be used to locate and use plugins within your own library
You should never edit these files.

To see examples of how a package can make use of these registry files, please refer to
`GeoIPS' documentation <https://github.com/NRLMMD-GEOIPS/geoips/tree/main/docs/source>`_.

This package defaults to the ``geoips.plugin_packages`` namespace.
It contains all plugin packages registered under GeoIPS.
You may specify a different name space.

You can pass ``--packages`` to limit the plugins processed.

JSON files are output by default.
You may also output yaml files for ease of viewing by passing ``--save-type yaml``.

For example:

::

    pluginify create
    pluginify create --packages geoips geoips_clavrx
    pluginify create --save-type yaml
    pluginify create --namespace <different_namespace>

.. _pluginify_delete:

pluginify delete
================

:ref:`pluginify delete <pluginify_delete>`

``pluginify delete`` removes the plugin registry files.
If no registry files are found, nothing occurs. For example:

::

    pluginify delete
    pluginify delete --packages geoips geoips_clavrx
    pluginify delete --namespace <different_namespace>

