# # # This source code is subject to the license referenced at
# # # https://github.com/NRLMMD-GEOIPS.

"""Context managers for handling optional dependencies throughout pluginify."""

import logging
from contextlib import contextmanager
import traceback
from typing import Generator

LOG = logging.getLogger(__name__)


@contextmanager
def import_optional_dependencies(loglevel: str = "info") -> Generator[None, None, None]:
    """Attempt to import a package and log the event if the import fails.

    Use as a context manager wrapping potentially-failing imports:

    .. code-block:: python

        with import_optional_dependencies():
            import some_optional_package

    Parameters
    ----------
    loglevel : str, optional
        Name of the log level to write to. May be any valid log level (e.g.
        ``"debug"``, ``"info"``, etc.). Defaults to ``"info"``.

    Yields
    ------
    None
        Does not yield a value; the wrapped block executes in-place.
    """
    try:
        yield None
    except ImportError as err:
        tb = traceback.extract_tb(err.__traceback__)
        filename, lineno, _, _ = tb[-1]
        err_str = f"Failed to import {err.name} at {filename}:{lineno}. "
        err_str += "If you need it, install it."

        getattr(LOG, loglevel)(err_str)