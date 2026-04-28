    # # # This source code is subject to the license referenced at
    # # # https://github.com/NRLMMD-GEOIPS.

Pluginify
=========

This repository contains everything necessary to fully register YAML and python classes
and/or modules as valid python plugin objects. A YAML-based plugin object essentially
acts as a configuration object for a class / module -based python plugin. The python
based plugins are then responsible for reading, manipulating, or outputting a dataset
in a certain format. For most python based plugins, we expect this dataset to be a valid
xarray.DataTree object.

No valid plugins should be stored in this package. Rather, this package contains all the
functionality to register, retrieve, and create your plugin objects via a unified
PluginRegistry class. This package can and is used alongside other packages such as
[GeoIPS](https://github.com/NRLMMD-GEOIPS/geoips) to handle their plugin-based
infrastructure.

Install pluginify package
-------------------------
Current status:
```bash
git clone https://github.com/NRLMMD-GEOIPS/pluginify.git
# cd to pluginify's top level dir
pip install -e .
```
OR
```bash
pip install pluginify
```

Use pluginify
-------------
```bash
pluginify -h
# Top level commands without additional args
pluginify create
# OR
pluginify delete
```
