"""Commandline module for Pluginify.

Supports two commands, `pluginify create` and `pluginify delete`. These create/ delete
plugin registries for one or more packages under a given namespace of a certain file
type [.json, .yaml]. If deleting, both file types are deleted if found.
"""

from argparse import ArgumentParser

from pluginify.plugin_registry import PluginRegistry


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
        required=True,
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
        "--package_name",
        type=str.lower,
        default=None,
        help="Package name to create registries for. If not specified, run on all.",
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


if __name__ == "__main__":
    parser = get_parser()
    ARGS = parser.parse_args()

    plugin_registry = PluginRegistry(namespace=ARGS.namespace)

    if ARGS.mode == "delete":
        plugin_registry.delete_registries(packages=ARGS.packages)
    else:
        plugin_registry.create_registries(
            packages=ARGS.packages, save_type=ARGS.save_type
        )
