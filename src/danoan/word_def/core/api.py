import importlib
import pkgutil
from typing import Any, List


def register_plugins():
    # Taverse the modules contained in
    # the plugins namespace call the
    # function get_language of each of them
    # and register the module names in a dictionary.
    # I would like to call get_language without having
    # to import the module. Or, at least, call it once,
    # drop it from memory and then create a LazyLoader for it.
    pass


def get_adapter(language_code: str) -> List[Any]:
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
