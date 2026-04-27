:orphan:

```{dropdown} Distribution Statement

| # # # This source code is subject to the license referenced at
| # # # https://github.com/NRLMMD-GEOIPS.

```

(configuration)=

# Pluginify Configuration System

Pluginify's behaviour at runtime is governed by three configuration variables.
These variables determine which plugin packaging namespace to search, whether
missing registries should be automatically rebuilt, and where registry cache
files are written.

## Configuration Variables

| Variable | Default | Description |
|---|---|---|
| `NAMESPACE` | `pluginify.plugin_packages` | Entry-point namespace in which plugin packages are discovered |
| `REBUILD_REGISTRIES` | `True` | Whether to automatically rebuild missing plugin registries at runtime |
| `REGISTRY_DIRECTORY` | `~/.cache/{env_name}` | Base directory where registry files are cached |

## Resolution Priority

Configuration values are resolved in the following priority order (highest to lowest):

1. **Environment variables** — set via `PLUGINIFY_*` environment variables.
2. **Config file** — stored at `~/.config/pluginify/config.yaml`.
3. **Hardcoded defaults** — the defaults shown in the table above.

Environment variables always override values from the config file or defaults.

## Configuration File

Pluginify uses `platformdirs` to locate the configuration file. This ensures
the config path follows platform-appropriate conventions on Linux, macOS, and
Windows.

The config file is expected at:

```text
~/.config/pluginify/config.yaml
```

If present, pluginify loads the following keys from the YAML file:

- `NAMESPACE`
- `REBUILD_REGISTRIES`
- `REGISTRY_DIRECTORY`

Any keys not present fall back to their defaults.

## CLI Configuration Commands

Pluginify's command-line interface provides the `pluginify config` subcommand
for managing configuration values. These commands write directly to the
config file at `~/.config/pluginify/config.yaml`.

### Setting Configuration Values

```bash
pluginify config set namespace <value>
pluginify config set rebuild-registries <bool>
pluginify config set registry-directory <path>
```

### Displaying Current Configuration

Add a `-h` flag to any of the commands above to see additional help information:

```bash
pluginify config --help
```

## Environment Variables

Instead of (or in addition to) the config file, you can set configuration
values using environment variables. Add the following to your shell
configuration file (e.g. `~/.bashrc`, `~/.zshrc`, `~/.profile`):

```bash
export PLUGINIFY_NAMESPACE='your_namespace'
export PLUGINIFY_REBUILD_REGISTRIES='True'
export PLUGINIFY_REGISTRY_DIRECTORY='/path/to/dir'
```

Environment variables take precedence over both the config file and hardcoded
defaults, making them useful for temporary overrides or containerized
environments.

## Cache Isolation

The default `REGISTRY_DIRECTORY` is `~/.cache/{env_name}`, where `{env_name}`
is automatically detected from the active Python environment. Pluginify
supports detection of:

- **Conda / Mamba** environments via the `CONDA_DEFAULT_ENV` environment
  variable.
- **venv / virtualenv** environments via `sys.prefix` or `VIRTUAL_ENV`.
- **Base environment** — falls back to `base_env` when no virtual environment
  is detected.

This ensures that plugin registries from different environments are cached
separately, preventing conflicts when switching between projects.
