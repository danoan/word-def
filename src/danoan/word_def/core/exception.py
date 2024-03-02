"""
Exceptions raised by API.
"""


class UnexpectedResponseError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message


class ConfigurationFileRequiredError(Exception):
    pass


class PluginNotAvailableError(Exception):
    pass


class PluginMethodNotImplementedError(Exception):
    def __init__(self, method_name: str):
        self.method_name = method_name

    def __str__(self):
        return f"The method `{self.method_name}` is not implemented in this version of the plugin. Consider updating it to a different version."


class UnrecognizedPluginModule(Exception):
    pass
