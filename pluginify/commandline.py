"""Commandline module for Pluginify.

Supports two commands, `pluginify create` and `pluginify delete`. These create/ delete
plugin registries for one or more packages under a given namespace of a certain file
type [.json, .yaml]. If deleting, both file types are deleted if found.
"""

from argparse import ArgumentParser
import logging
import sys

from pluginify.plugin_registry import PluginRegistry


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


def get_parser():
    """Create the ArgumentParser for main."""
    description = (
        "Creates Plugin Registries for all installed GeoIPS packages. "
        "The registries will be written to the root directory of each installed "
        "package. The registries will be named either 'registered_plugins.json' "
        "or 'registered_plugins.yaml' depending on which format is chosen. "
        "For additional information on GeoIPS plugin registries please refer to "
        "the GeoIPS documentation."
    )
    parser = ArgumentParser(
        prog="pluginify",
        description=description,
    )
    parser.add_argument(
        "mode",
        type=str.lower,
        choices=["create", "delete"],
        help="Pluginify mode. Create or delete plugin registries.",
    )
    parser.add_argument(
        "-s",
        "--save_type",
        type=str.lower,
        default="json",
        choices=["json", "yaml"],
        help="Format to write registries to. This will also be the file extension.",
    )
    parser.add_argument(
        "-p",
        "--packages",
        default=None,
        nargs="+",
        type=str,
        help=(
            "The plugin packages to create or delete plugin registries for. Defaults to"
            " None. If None, all plugin packages under 'namespace' will have their "
            "plugin registries created or deleted, based on the command supplied."
        ),
    )
    parser.add_argument(
        "-n",
        "--namespace",
        type=str,
        default="geoips.plugin_packages",
        help=(
            "Namespace that your plugin packages fall under. Defaults to geoips, but a "
            "user can create separate namespaces if developing interfaces outside of "
            "the main GeoIPS package."
        ),
    )
    return parser


def main():
    """Entrypoint function for pluginify's CLI."""
    parser = get_parser()
    ARGS = parser.parse_args()
    configure_logging(logging.INFO)

    plugin_registry = PluginRegistry(namespace=ARGS.namespace)

    if ARGS.mode == "delete":
        plugin_registry.delete_registries(packages=ARGS.packages)
    else:
        plugin_registry.create_registries(
            packages=ARGS.packages, save_type=ARGS.save_type
        )


if __name__ == "__main__":
    main()
