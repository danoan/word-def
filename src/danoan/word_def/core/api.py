import importlib
import pkgutil
from typing import Any, List

plugin_register = {}


def register_plugins():
    # TODO: Consider using LazyLoader
    prefix = "danoan.word_def.plugins.modules"
    plugins_module = importlib.import_module(prefix)
    for module_info in pkgutil.iter_modules(plugins_module.__path__, prefix=f"{prefix}."):
        print(module_info)
        module = importlib.import_module(module_info.name)
        factory = module.AdapterFactory()
        plugin_register[factory.get_language()] = factory.get_adapter


def get_adapter(language_code: str) -> List[Any]:
    # TODO: Display a message if someone tries do get an adapter
    # but there is nothing in plugins.modules (needs to install at
    # least one plugin package)
    # This will access the plugins register and pick
    # the proper adapter.
    prefix = "danoan.word_def.plugins"
    plugins_module = importlib.import_module(prefix)
    for module_info in pkgutil.iter_modules(
        plugins_module.__path__, prefix=f"{prefix}."
    ):
        print(module_info.name)
        module = importlib.import_module(module_info.name)
        print(module.get_language())


def get_definition(word: str, language_code: str) -> List[str]:
    adapter = get_adapter(language_code)[0]
    return adapter.get_definition(word)
