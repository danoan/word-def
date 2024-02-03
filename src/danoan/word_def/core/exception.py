class PluginNotAvailableError(Exception):
    pass


class PluginMethodNotImplementedError(Exception):
    def __init__(self, method_name: str):
        self.method_name = method_name

    def __str__(self):
        return f"The method `{self.method_name}` is not implemented in this version of the plugin. Consider updating it to a different version."
