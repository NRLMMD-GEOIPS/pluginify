# # # This source code is subject to the license referenced at
# # # https://github.com/NRLMMD-GEOIPS.

"""Pluginify error module."""


class PluginError(Exception):
    """Exception to be raised when there is an error in a plugin."""

    pass


class PluginRegistryError(Exception):
    """Exception to be raised when there is an error in a plugin registry."""

    pass


class PluginValidationError(PluginError):
    """Exception raised when a plugin fails schema/pydantic validation."""

    def __init__(self, plugin_name, interface_name, package, abspath, pydantic_exc):
        self.plugin_name = plugin_name
        self.interface_name = interface_name
        self.package = package
        self.abspath = abspath
        self.pydantic_exc = pydantic_exc
        super().__init__(self._build_message())

    def _build_message(self):
        summary = self._summarize_errors(self.pydantic_exc)
        return (
            f"Validation failed for {self.interface_name} plugin "
            f"'{self.plugin_name}' "
            f"(package: '{self.package}', file: '{self.abspath}').\n{summary}"
        )

    @staticmethod
    def _summarize_errors(exc):
        errors = exc.errors()
        field_errors = {}
        for err in errors:
            field = ".".join(str(loc) for loc in err["loc"] if not isinstance(loc, int))
            if field not in field_errors:
                field_errors[field] = []
            field_errors[field].append(err["msg"])

        lines = [f"  {len(errors)} error(s) found. Summary by field:"]
        for field, msgs in field_errors.items():
            unique_msgs = list(dict.fromkeys(msgs))
            lines.append(f"    - {field}: {'; '.join(unique_msgs)}")
        return "\n".join(lines)
