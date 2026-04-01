"""Commandline module for Pluginify.

Supports two commands, `pluginify create` and `pluginify delete`. These create/ delete
plugin registries for one or more packages under a given namespace of a certain file
type [.json, .yaml]. If deleting, both file types are deleted if found.
"""

import logging
from typing import List, Literal, Optional
import sys
from types import SimpleNamespace

import typer

from pluginify.plugin_registry import PluginRegistry

app = typer.Typer()


def configure_logging(level=logging.INFO):
    """Configure root logging for the command-line interface.

    This function attaches a StreamHandler to the root logger so that all log
    messages emitted by this process—including logs from imported modules,
    dynamically loaded plugins, and third-party libraries—are routed to the
    terminal.

    Logging is configured only once. If handlers are already attached to the
    root logger, this function exits without making changes to avoid duplicate
    log output.

    Parameters
    ----------
    level : int, optional
        Logging level to apply to the root logger and handler. Defaults to
        logging.INFO. Common values include logging.DEBUG, logging.INFO,
        logging.WARNING, and logging.ERROR.

    Returns
    -------
    None
    """
    root = logging.getLogger()

    # Avoid duplicate handlers if CLI is called multiple times
    if root.handlers:
        return

    root.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(levelname)s | %(name)s | %(message)s")
    handler.setFormatter(formatter)

    root.addHandler(handler)


HELP_MESSAGES = SimpleNamespace(
    **{
        "namespace": "The namespace which plugin packages are registered under.",
        "packages": (
            "A list of strings representing plugin packages to create registries for. "
            "If None, create registry files for all plugin packages found under "
            "``namespace``"
        ),
        "save_type": (
            "The file extension to save the registry files as. Defaults to ``json``, "
            "``yaml`` can be specified as well."
        ),
    }
)
ARGUMENTS = SimpleNamespace(
    **{
        "namespace": typer.Option(
            "geoips.plugin_packages", "--namespace", "-n", help=HELP_MESSAGES.namespace
        ),
        "packages": typer.Option(None, "--packages", "-p", help=HELP_MESSAGES.packages),
        "save_type": typer.Option(
            "json", "--save-type", "-s", help=HELP_MESSAGES.save_type
        ),
    },
)


@app.command()
def create(
    namespace: str = ARGUMENTS.namespace,
    packages: Optional[List[str]] = ARGUMENTS.packages,
    save_type: Literal["json", "yaml"] = ARGUMENTS.save_type,
):
    """Create plugin registry files for one or more packages under a given namespace."""
    plugin_registry = PluginRegistry(namespace=namespace)
    plugin_registry.create_registries(packages=packages, save_type=save_type)


@app.command()
def delete(
    namespace: str = ARGUMENTS.namespace,
    packages: Optional[List[str]] = ARGUMENTS.packages,
):
    """Delete plugin registry files for one or more packages under a given namespace."""
    plugin_registry = PluginRegistry(namespace=namespace)
    plugin_registry.delete_registries(packages=packages)


def main():
    """Entrypoint function for pluginify's CLI."""
    configure_logging(logging.INFO)
    app()
