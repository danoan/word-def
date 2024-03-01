from danoan.word_def.core import api, exception, model

import io
import functools
from pathlib import Path
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


def test_plugin_register():
    plugins_location = f"{SCRIPT_FOLDER}/input"
    plugins_base_import_path = "danoan.word_def.plugins.modules"

    @plugin_context(plugins_location, plugins_base_import_path)
    def inner():
        register = api.get_register()

        language_plugins = register.get_language_plugins("eng")
        assert len(language_plugins) == 1
        assert (
            language_plugins[0].package_name
            == f"{plugins_base_import_path}.fake_dictionary_english"
        )

    inner()


def test_get_definition():
    plugins_location = f"{SCRIPT_FOLDER}/input"
    plugins_base_import_path = "danoan.word_def.plugins.modules"

    plugin_configuration = {"secret_key": "my_secret"}
    ss = io.StringIO()
    toml.dump(plugin_configuration, ss)
    ss.seek(0, io.SEEK_SET)

    @plugin_context(plugins_location, plugins_base_import_path)
    def inner():
        list_of_definitions = api.get_definition(
            "happy", "eng", configuration_stream=ss
        )
        assert len(list_of_definitions) > 0
        assert list_of_definitions[0] == "State of joy."

    inner()
