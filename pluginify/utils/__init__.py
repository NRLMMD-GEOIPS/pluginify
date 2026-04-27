# # # This source code is subject to the license referenced at
# # # https://github.com/NRLMMD-GEOIPS.

"""Utility functions for pluginify.

Provides generic helpers used throughout the package:

- ``merge_nested_dicts`` — recursively merge two dictionaries while
  preserving existing values in the destination.

See Also
--------
pluginify.utils.validators : Plugin registry validation helpers.
pluginify.utils.context_managers : Optional import context manager.
"""

from copy import deepcopy


def merge_nested_dicts(dest: dict, src: dict, in_place: bool = True, replace: bool = False) -> dict | None:
    """Merge ``src`` into ``dest`` recursively.

    Performs an in-place merge of ``src`` into ``dest`` while preserving any values
    that already exist in ``dest``. If ``replace`` is ``True``, matching keys in
    ``dest`` are overwritten by ``src`` instead.

    Parameters
    ----------
    dest : dict
        The destination dictionary to merge to.
    src : dict
        The source dictionary to merge into ``dest``.
    in_place : bool, optional
        Whether to merge directly into ``dest`` (``True``) or to create a deepcopy
        of ``dest`` and return that as the result (``False``). Defaults to ``True``.
    replace : bool, optional
        Whether to override duplicate keys in ``dest`` with the contents of
        ``src``. Defaults to ``False``.

    Returns
    -------
    dict or None
        The merged dict when ``in_place`` is ``False``, or ``None`` when
        ``in_place`` is ``True``.
    """
    if not in_place:
        final_dest = deepcopy(dest)
    else:
        final_dest = dest

    # It will automatically replace ALL fields found in
    # the original product spec and also found in the
    # override with what is specified in the override
    # in its entirety, without merging.  This is not
    # terribly useful overall - we probably want this
    # sort of capability in the end, but more flexible
    # and able to be applied to only specific fields,
    # etc.  This is a brute force method to at least
    # allow overriding entire fields.
    if replace:
        for key in final_dest:
            if key in src:
                final_dest[key] = src[key]
        return final_dest

    try:
        final_dest.update(src | final_dest)
    except (AttributeError, TypeError):
        return
    try:
        for key, val in final_dest.items():  # NOQA
            try:
                merge_nested_dicts(final_dest[key], src[key])
            except KeyError:
                pass
    except AttributeError:
        raise
    if not in_place:
        return final_dest