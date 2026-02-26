# # # This source code is subject to the license referenced at
# # # https://github.com/NRLMMD-GEOIPS.

"""Pluginify utility module."""

from copy import deepcopy


def merge_nested_dicts(dest, src, in_place=True, replace=False):
    """Perform an in-place merge of src into dest.

    Performs an in-place merge of src into dest while preserving any values that already
    exist in dest.

    Parameters
    ----------
    dest: dict
        - The destination dictionary to merge to
    src: dict
        - The source dictionary to merge into dest
    in_place: bool, default=True
        - Whether or not to merge directly into dest or to create a deepcopy of dest
          and return that as the final result. By default, this function will merge
          directly into dest.
    replace: boo, default=False
        - Whether or not to override duplicate keys in src and dest with the contents of
          src. By default, replace is set to false and overriding will not occur.
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
