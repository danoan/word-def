from danoan.word_def.core import api, exception, model

import io
import functools
from pathlib import Path
import pytest
import shutil
import sys
import tempfile
import toml

SCRIPT_FOLDER = Path(__file__).parent


def plugin_context(plugins_location, plugins_base_import_path):
    def decorator(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            with tempfile.TemporaryDirectory() as tempdir:
                sys.path.append(tempdir)

                plugin_temp_location = functools.reduce(
                    lambda x, y: x / y,
                    [Path(tempdir)] + plugins_base_import_path.split("."),
                )

                plugin_temp_location.mkdir(parents=True)

                input_folder = Path(plugins_location)
                for path in input_folder.iterdir():
                    if path.is_file():
                        shutil.copy2(path, plugin_temp_location / path.name)

                func(*args, **kwargs)

        return inner

    return decorator


@pytest.mark.parametrize(
    "language_code,list_plugins_name",
    [
        ("eng", ["fake_dictionary_english", "fake_multilanguage"]),
        ("fra", ["fake_multilanguage"]),
    ],
)
def test_plugin_register(language_code, list_plugins_name):
    plugins_location = f"{SCRIPT_FOLDER}/input"
    plugins_base_import_path = "danoan.word_def.plugins.modules"

    @plugin_context(plugins_location, plugins_base_import_path)
    def inner():
        register = api.get_register()

        language_plugins = register.get_language_plugins(language_code)
        assert len(language_plugins) == len(list_plugins_name)
        for plugin in language_plugins:
            assert (
                plugin.package_name.split(f"{plugins_base_import_path}.")[1]
                in list_plugins_name
            )

    inner()


@pytest.mark.parametrize(
    "word,language_code,definition",
    [
        ("happy", "eng", "State of joy."),
        ("joyeux", "fra", "Qui éprouve de la joie, qui est gai."),
    ],
)
def test_get_definition(word, language_code, definition):
    plugins_location = f"{SCRIPT_FOLDER}/input"
    plugins_base_import_path = "danoan.word_def.plugins.modules"

    plugin_configuration = {"secret_key": "my_secret"}
    ss = io.StringIO()
    toml.dump(plugin_configuration, ss)
    ss.seek(0, io.SEEK_SET)

    @plugin_context(plugins_location, plugins_base_import_path)
    def inner():
        list_of_definitions = api.get_definition(
            word, language_code, configuration_stream=ss
        )
        assert len(list_of_definitions) > 0
        assert list_of_definitions[0] == definition

    inner()


def test_versions():
    plugins_location = f"{SCRIPT_FOLDER}/input"
    plugins_base_import_path = "danoan.word_def.plugins.modules"

    @plugin_context(plugins_location, plugins_base_import_path)
    def inner():
        register = api.get_register()

        english_plugin = register.get_language_plugins("eng")[0]
        english_plugin_2 = register.get_language_plugins("eng")[1]
        french_plugin = register.get_language_plugins("fra")[0]

        assert api.is_plugin_compatible(english_plugin.adapter_factory)
        assert api.is_plugin_compatible(english_plugin_2.adapter_factory)
        assert api.is_plugin_compatible(french_plugin.adapter_factory)

    inner()
