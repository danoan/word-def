from danoan.word_def.core import api, exception

import io
from pathlib import Path
from textwrap import dedent
import toml
from typing import Optional


def get_plugin_name(language_code: str) -> str:
    register = api.get_register()
    if len(register.get_language_plugins(language_code)) == 0:
        print(f"No plugin registered for language `{language_code}`.")
        exit(1)

    return register.get_language_plugins(language_code)[0].package_name


def get_configuration_stream(
    plugin_name: str, plugin_configuration_filepath: Optional[Path]
) -> Optional[io.TextIOBase]:
    if plugin_configuration_filepath is None:
        return None

    plugin_config = toml.load(plugin_configuration_filepath)

    if plugin_name not in plugin_config:
        print(f"There is no `{plugin_name}` in the plugin configuration file. Exiting.")
        exit(1)

    plugin_configuration_dict = plugin_config[plugin_name]

    ss = io.StringIO()
    toml.dump(plugin_configuration_dict, ss)
    ss.seek(0)

    return ss


def pluging_not_available_error_message(language_code: str) -> str:
    return dedent(
        f"""
        There is no plugin available for the language with code `{language_code}`.
        Make sure that you have installed the plugin package (e.g.
        word-def-plugin-english-collins) and that you have the correct language code.
        It should be the three letter ISO 639-2 code (e.g. `eng`)
        """
    )


def plugin_method_not_implemented_error_message(
    ex: exception.PluginMethodNotImplementedError,
) -> str:
    return dedent(
        f"""
        The method {ex.method_name} is not implemented for the requested language plugin or
        the plugin has an error. Make sure that you have a updated version installed.
        """
    )


def configuration_file_required_error_message() -> str:
    return dedent(
        f"""
        The plugin requires a configuration file that was not specified.
        Make sure to pass the configuration file using the flag
        `--plugin-configuration-filepath`.
        """
    )
