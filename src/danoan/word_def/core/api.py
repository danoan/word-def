"""
Public API.
"""

from danoan.word_def.core import exception, model

from functools import wraps
import importlib
import logging
import pkgutil
import sys
from typing import Callable, Dict, List, Optional, TextIO

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))

T_Register = Dict[str, List[model.Plugin]]


class _PluginRegister:
    """
    Language dictionaries plugin register.

    Internal class that holds a dictionary with references to
    installed word-def plugins package.
    """

    def __init__(self):
        self.plugin_register: T_Register = {}
        self.languages_available = set()

        for module, module_name in self._collect_plugin_modules():
            try:
                factory = module.AdapterFactory()
            except AttributeError:
                logger.info(
                    f"The module {module_name} does not seem to have an AdapterFactory function and thus cannot be registered as a plugin. Skipping it."
                )
                continue

            plugin = model.Plugin(module_name, factory)

            language = factory.get_language()
            if language not in self.plugin_register:
                self.plugin_register[language] = []

            self.plugin_register[language].append(plugin)
            self.languages_available.add(language)

    def _collect_plugin_modules(self):
        """
        Collect all modules found in the word-def plugin namespace.
        """
        # TODO: Consider using LazyLoader
        prefix = "danoan.word_def.plugins.modules"
        plugins_module = importlib.import_module(prefix)
        for module_info in pkgutil.iter_modules(
            plugins_module.__path__, prefix=f"{prefix}."
        ):
            yield importlib.import_module(module_info.name), module_info.name

    def get_language_plugins(self, language_code: str) -> List[model.Plugin]:
        """
        Return a list of registered adapters for the requested language.
        """
        if language_code not in self.languages_available:
            return []

        return self.plugin_register[language_code]


def _get_register() -> Callable[[], "PluginRegister"]:
    register = None

    def get_register() -> PluginRegister:
        """
        Get public proxy do _PluginRegister.
        """
        nonlocal register
        if register is None:
            register = PluginRegister(_PluginRegister())
        return register

    return get_register


def _get_plugin_by_index(language_code: str, index: int) -> Optional[model.Plugin]:
    register = get_register()
    list_of_plugins = register.get_language_plugins(language_code)
    if index < len(list_of_plugins):
        return list_of_plugins[index]
    return None


def _get_plugin_by_name(language_code: str, name: str) -> Optional[model.Plugin]:
    register = get_register()

    for plugin in register.get_language_plugins(language_code):
        if plugin.package_name == name:
            return plugin
    return None


def _get_plugin(language_code: str, plugin_name: Optional[str] = None) -> model.Plugin:
    """
    Get the most appropriate plugin available.

    This is the order of preference followed by this function:

    1. plugin named plugin_name and registered with language_code.
    2. the first plugin registered with language_code.
    3. raises PluginNotAvailableError

    Raises:
        PluginNotAvailableError: If there is no plugin registered for the requested language.
        ConfigurationFileRequiredError: If the language adapter needs a configuration file but the latter was not given.
    """

    if plugin_name:
        plugin = _get_plugin_by_name(language_code, plugin_name)
    else:
        plugin = _get_plugin_by_index(language_code, 0)

    if not plugin:
        raise exception.PluginNotAvailableError()

    return plugin


def _check_missing_implementation(method_name: str):
    def inner(api_function):
        @wraps(api_function)
        def wrapper(*args, **kwargs):
            try:
                return api_function(*args, **kwargs)
            except AttributeError as ex:
                raise exception.PluginMethodNotImplementedError(
                    method_name=method_name
                ) from ex

        return wrapper

    return inner


# -------------------- API Functions --------------------


class PluginRegister:
    """
    Public proxy to _PluginRegister.
    """

    def __init__(self, plugin_register: _PluginRegister):
        self._plugin_register = plugin_register

    def get_language_plugins(self, language_code: str) -> List[model.Plugin]:
        """
        Return a list of registered adapters for the requested language.
        """
        return self._plugin_register.get_language_plugins(language_code)


get_register = _get_register()


@_check_missing_implementation("get_definition")
def get_definition(
    word: str,
    language_code: str,
    plugin_name: Optional[str] = None,
    configuration_stream: Optional[TextIO] = None,
) -> List[str]:
    """
    Get a list of definitions for the given word.
    """
    plugin = _get_plugin(language_code, plugin_name)
    adapter = plugin.adapter_factory.get_adapter(configuration_stream)
    return adapter.get_definition(word)


@_check_missing_implementation("get_pos_tag")
def get_pos_tag(
    word: str,
    language_code: str,
    plugin_name: Optional[str] = None,
    configuration_stream: Optional[TextIO] = None,
):
    """
    Get a list of part-of-speech tags for the given word.
    """
    plugin = _get_plugin(language_code, plugin_name)
    adapter = plugin.adapter_factory.get_adapter(configuration_stream)
    return adapter.get_pos_tag(word)


@_check_missing_implementation("get_synonyme")
def get_synonyme(
    word: str,
    language_code: str,
    plugin_name: Optional[str] = None,
    configuration_stream: Optional[TextIO] = None,
):
    """
    Get a list of synonymes to the given word.
    """
    plugin = _get_plugin(language_code, plugin_name)
    adapter = plugin.adapter_factory.get_adapter(configuration_stream)
    return adapter.get_synonyme(word)


@_check_missing_implementation("get_usage_examples")
def get_usage_examples(
    word: str,
    language_code: str,
    plugin_name: Optional[str] = None,
    configuration_stream: Optional[TextIO] = None,
):
    """
    Get a list of examples in which the given word is employed.
    """
    plugin = _get_plugin(language_code, plugin_name)
    adapter = plugin.adapter_factory.get_adapter(configuration_stream)
    return adapter.get_usage_examples(word)
