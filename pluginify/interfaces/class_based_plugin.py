"""Implements a base class for class-based plugins.

The base class implemented here would expose the call signature of the child plugin
class as ``__call__()`` while also providing hooks for pre- and post-processing.

The hooks are available as ``_pre_call()`` and ``_post_call()``. They should be used to
implement common functionality that all plugins of this type should posess but which we
don't want developers to need to implement. They are intended to be overridden by the
child plugin-type class (e.g. ``BaseReaderPlugin``). They should define what kwargs they
accept when defined on the plugin-type class but should accept their arguments from
``**kwargs`` from ``__call__()``.

The ``call()`` method should be overridden on the actual plugin class. It should provide
the data processing for the plugin. ``__call__()``'s signature will be identical to that
of ``call()`` except that ``call()`` should not accept ``**kwargs``. That should be
consumed by the hooks.

``__call__()`` should not be overridden anywhere.

Required attributes
-------------------
interface : str
    The interface type the plugin belongs to
    (e.g. ``'configs'``, ``'data_modifiers'``).
    This is typically provided by the interface-level plugin class and not the
    individual plugin class.
family : str
    The family name of the plugin. This should be defined by the plugin class.
name : str
    The specific name of the plugin. This should be defined by the plugin class.

Required methods
----------------
call()
    The main method that performs the plugin's functionality. This method
    should be implemented by the plugin class.
_pre_call()
    A hook method that can be overridden to preprocess data before
    calling the main ``call()`` method. This method should accept the same
    arguments as ``call()`` via ``*args`` and ``**kwargs`` and should,
    typically, be implemented by the interface-level plugin class.
_post_call()
    A hook method that can be overridden to post-process data after
    calling the main ``call()`` method. This method should accept the same
    arguments as ``call()`` via ``*args`` and ``**kwargs`` and should,
    typically, be implemented by the interface-level plugin class.

Notes
-----
The purpose of ``_pre_call()`` and ``_post_call()`` is to allow for common
functionality that all plugins of a certain type should possess, without requiring
developers to implement this functionality in every plugin class. Initially, this
will be used to convert inputs from DataTree to other formats and back to DataTree
after processing, but it could be used for other common tasks as well.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
import functools
import inspect
from typing import Any


def valid_str_attr(cls: type, attr_name: str) -> None:
    """Check that the given attribute is a non-empty string.

    Parameters
    ----------
    cls : type
        The class whose attribute should be checked.
    attr_name : str
        The name of the attribute to check.

    Raises
    ------
    TypeError
        If the attribute is not a string.
    ValueError
        If the attribute is an empty string.
    """
    attr_value = getattr(cls, attr_name, None)
    if not isinstance(attr_value, str):
        raise TypeError(f"{cls.__name__}.{attr_name} must be a string")
    if not attr_value:
        raise ValueError(f"{cls.__name__}.{attr_name} cannot be empty")


class BaseClassPlugin(ABC):
    """The base class for class-based plugins.

    All plugins are required to carry the following class attributes:

    interface : str
        The interface type the plugin belongs to
        (e.g. ``'configs'``, ``'data_modifiers'``).
        This is typically provided by the interface-level plugin class and not the
        individual plugin class.
    family : str
        The family name of the plugin. This should be defined by the plugin class.
    name : str
        The specific name of the plugin. This should be defined by the plugin class.

    Subclasses of this base class must also implement the following methods:

    call()
        The main method that performs the plugin's functionality. This method
        should be implemented by the plugin class.
    _pre_call()
        A hook method that can be overridden to preprocess data before
        calling the main ``call()`` method. This method should accept the same
        arguments as ``call()`` via ``*args`` and ``**kwargs`` and should,
        typically, be implemented by the interface-level plugin class.
    _post_call()
        A hook method that can be overridden to post-process data after
        calling the main ``call()`` method. This method should accept the same
        arguments as ``call()`` via ``*args`` and ``**kwargs`` and should,
        typically, be implemented by the interface-level plugin class.

    Notes
    -----
    The purpose of ``_pre_call()`` and ``_post_call()`` is to allow for common
    functionality that all plugins of a certain type should possess, without requiring
    developers to implement this functionality in every plugin class. Initially, this
    will be used to convert inputs from DataTree to other formats and back to DataTree
    after processing, but it could be used for other common tasks as well.
    """

    # If set to True, we are in OBP. False means we are in a legacy procflow.
    # Set up logic in this or interface classes to convert from DT to data type
    # referenced in family

    # If no family is provided, just assume it works with DT
    data_tree = False
    required_attributes = ["interface", "family", "name"]

    def _check_interface_attribute(cls):
        """Check that the 'interface' attribute is valid.

        Ensures the attribute is a non-empty string and a known plugin interface.

        Parameters
        ----------
        cls : type
            The class whose interface attribute should be checked.
        """
        valid_str_attr(cls, "interface")

    def _check_family_attribute(cls):
        """Check that the 'family' attribute is valid.

        Ensures the attribute is a non-empty string.

        Parameters
        ----------
        cls : type
            The class whose family attribute should be checked.
        """
        valid_str_attr(cls, "family")

    def _check_name_attribute(cls):
        """Check that the 'name' attribute is valid.

        Ensures the attribute is a non-empty string.

        Parameters
        ----------
        cls : type
            The class whose name attribute should be checked.
        """
        valid_str_attr(cls, "name")

    @abstractmethod
    def call(self, *args: Any, **kwargs: Any) -> Any:
        """Callable method to be implemented by the plugin class.

        Returns
        -------
        Any
            The result of the plugin's processing.
        """
        pass

    # hooks are intentionally loose; document their accepted kwargs
    def _pre_call(self, data: Any = None, *args: Any, **kwargs: Any) -> Any:
        """Preprocess the data before calling the main plugin method.

        Parameters
        ----------
        data : Any
            The input data for the plugin.

        Returns
        -------
        Any
            The processed data.
        """
        return data

    def _post_call(self, data: Any = None, *args: Any, **kwargs: Any) -> Any:
        """Post-process the data after calling the main plugin method.

        Parameters
        ----------
        data : Any
            The output data from the plugin.

        Returns
        -------
        Any
            The processed data.
        """
        return data

    def _invoke(self, data: Any = None, *args: Any, **kwargs: Any) -> Any:
        """Invoke the plugin's processing pipeline.

        If data is provided, runs the full ``_pre_call()`` → ``call()`` →
        ``_post_call()`` pipeline. Otherwise, delegates directly to ``call()``.

        Parameters
        ----------
        data : Any, optional
            The input data for the plugin. If ``None``, ``call()`` is invoked
            directly with ``*args`` and ``**kwargs``.

        Returns
        -------
        Any
            The result of the plugin's processing pipeline.
        """
        if data is None:
            data = self.call(*args, **kwargs)
        else:
            data = self._pre_call(data, *args, **kwargs)
            data = self.call(data, *args, **kwargs)
            data = self._post_call(data, *args, **kwargs)
        return data

    def __init__(self, module=None) -> None:
        """Initialize the plugin object.

        Parameters
        ----------
        module : ModuleType, optional
            The module from which the class-based plugin originated. This is used to
            collect metadata from the module and attach it to the plugin object. The
            metadata can then be used during validation to indicate where failing
            plugins originated. If ``None``, defaults are set.
        """
        if module:
            self.module_name = module.__name__
            self.module_path = module.__file__
        else:
            self.module_name = "Unknown."
            self.module_path = "Unknown."

    def __init_subclass__(cls, *, abstract: bool = False, **kwargs: Any) -> None:
        """Initialize a subclass of the plugin.

        Parameters
        ----------
        abstract : bool, optional
            If ``True``, the subclass is treated as abstract. When treated as
            abstract, validation is disabled in ``__init_subclass__``. Defaults to
            ``False``.

        Returns
        -------
        None

        Raises
        ------
        TypeError
            If the subclass does not define the required attributes.
        TypeError
            If the subclass does not implement the ``call()`` method.
        TypeError
            If the subclass overrides the ``__call__()`` method.
        """
        super().__init_subclass__(**kwargs)

        # Treat the root as abstract and honor explicit marker
        if cls is BaseClassPlugin or abstract:
            cls.__plugin_abstract__ = True
            return

        # Enforce required attributes and run attribute checkers if they exist
        for attr in cls.required_attributes:
            # Ensure required attributes are defined
            if not hasattr(cls, attr):
                raise TypeError(f"{cls.__name__} must define '{attr}' attribute")

            # Run attribute checker for the current attribute if it exists
            attribute_checker = getattr(cls, f"_check_{attr}_attribute", None)
            if attribute_checker is not None:
                attribute_checker(cls)

        # Prevent overriding __call__ in a True class-based plugin
        if "__call__" in cls.__dict__:
            raise TypeError(f"{cls.__name__} cannot override __call__")

        try:
            call_method = cls.__dict__.get("call")
        except AttributeError:
            raise TypeError(f"{cls.__name__} must implement call()")

        @functools.wraps(call_method)
        def _call(self, data: Any = None, *args: Any, **kwargs: Any) -> Any:
            return cls._invoke(self, data, *args, **kwargs)

        _call.__signature__ = inspect.signature(call_method)  # mirror only call()
        _call.__annotations__ = getattr(call_method, "__annotations__", {})
        cls.__call__ = _call