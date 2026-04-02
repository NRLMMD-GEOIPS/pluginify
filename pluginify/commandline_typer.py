"""Commandline module for Pluginify.

Supports two commands, `pluginify create` and `pluginify delete`. These create/ delete
plugin registries for one or more packages under a given namespace of a certain file
type [.json, .yaml]. If deleting, both file types are deleted if found.
"""

import logging
import inspect
import sys
from typing import List, Literal, Optional

import docstring_parser
import typer

from pluginify.config import NAMESPACE
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


class DocstringTyper(typer.Typer):
    """Subclass of typer.Typer that generates help messages from a command's docstring.

    Provided that a docstring has a 'parameters' section, all help messages for required
    or optional arguments will be automatically generated.

    Additionally, shorthand flags will be generated for all flag-based arguments. I.e.
    '--namespace' automatically generates a '-n' flag.
    """

    def command(self, *args, **kwargs):
        """Overridden typer.Typer:command decorator."""
        decorator = super().command(*args, **kwargs)

        def wrapper(func):
            """Generate help messages and shorthand aliases for all args of func."""
            sig = inspect.signature(func)
            doc = docstring_parser.parse(func.__doc__ or "")

            param_help = {p.arg_name: p.description for p in doc.params}

            # Replace docstring so Typer doesn't show the Parameters section
            new_doc = doc.short_description or ""
            if doc.long_description:
                new_doc += "\n\n" + doc.long_description

            func.__doc__ = new_doc

            new_params = []

            for name, param in sig.parameters.items():

                default = param.default

                if default is inspect._empty:
                    new_params.append(param)
                    continue

                help_text = param_help.get(name)

                short = f"-{name[0]}"
                long = f"--{name.replace('_','-')}"

                option = typer.Option(default, short, long, help=help_text)

                new_params.append(param.replace(default=option))

            new_sig = sig.replace(parameters=new_params)
            func.__signature__ = new_sig

            return decorator(func)

        return wrapper


app = DocstringTyper(context_settings={"help_option_names": ["-h", "--help"]})


@app.command()
def create(
    namespace: str = NAMESPACE,
    packages: Optional[List[str]] = None,
    save_type: Literal["json", "yaml"] = "json",
):
    """Create plugin registry files for one or more packages under a given namespace.

    Parameters
    ----------
    namespace: str, default='pluginify.plugin_packages'
        The namespace which plugin packages are registered under.
    packages: Optional[List[str]], default=None
        A list of strings representing plugin packages to create registries for. If
        None, create registry files for all plugin packages found under 'namespace'.
    save_type: Literal['json', 'yaml'], default='json'
        The file extension to save the registry files as. Defaults to 'json', 'yaml'
        can be specified as well.
    """
    plugin_registry = PluginRegistry(namespace=namespace)
    plugin_registry.create_registries(packages=packages, save_type=save_type)


@app.command()
def delete(
    namespace: str = NAMESPACE,
    packages: Optional[List[str]] = None,
):
    """Delete plugin registry files for one or more packages under a given namespace.

    Parameters
    ----------
    namespace: str, default='pluginify.plugin_packages'
        The namespace which plugin packages are registered under.
    packages: Optional[List[str]], default=None
        A list of strings representing plugin packages to create registries for. If
        None, create registry files for all plugin packages found under 'namespace'.
    """
    plugin_registry = PluginRegistry(namespace=namespace)
    plugin_registry.delete_registries(packages=packages)


def main():
    """Entrypoint function for pluginify's CLI."""
    configure_logging(logging.INFO)
    app()
