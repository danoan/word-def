from danoan.word_def.core import api, exception

import argparse
import io
from pathlib import Path
import toml
from typing import Optional


def __get_definition__(word: str, language_code: str, plugin_configuration_filepath: Optional[Path], plugin_name=Optional[str], *args, **kwargs):
    """
    Get definitions of a given word.
    """
    if plugin_name is None:
        register = api.get_register()
        if language_code not in register.languages_available:
            print(f"No plugin registered for language `{language_code}`.")
            exit(1)

        plugin_name = api.get_register(
        ).plugin_register[language_code][0].package_name

    plugin_config = toml.load(plugin_configuration_filepath)
    if plugin_name not in plugin_config:
        print(
            f"There is no `{plugin_name}` in the plugin configuration file. Exiting.")
        exit(1)

    plugin_configuration_dict = plugin_config[plugin_name]
    ss = io.StringIO()
    toml.dump(plugin_configuration_dict, ss)
    ss.seek(0)

    list_of_definitions = []
    try:
        list_of_definitions = api.get_definition(word, language_code,
                                                 configuration_stream=ss)
    except exception.PluginNotAvailableError:
        print(
            f"""
            There is no plugin available for the language with code `{language_code}`.
            Make sure that you have installed the plugin package (e.g.
            word-def-plugin-english-collins) and that you have the correct language code.
            It should be the three letter ISO 639-2 code (e.g. `eng`)
            """)
    except exception.PluginMethodNotImplementedError as ex:
        print(
            f"""
            The method {ex.method_name} is not implemented for the requested language plugin.
            Make sure that you have a updated version installed.
            """)
    else:
        for i, definition in enumerate(list_of_definitions, 1):
            print(f"{i}. {definition}")


def extend_parser(subparser_action=None):
    command = "get-definition"
    description = __get_definition__.__doc__
    help = description.split(".")[0]

    if subparser_action:
        parser = subparser_action.add_parser(command,
                                             help=help, description=description, formatter_class=argparse.RawTextHelpFormatter)
    else:
        parser = argparse.ArgumentParser(
            "Get word definitions", description=description, formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("word", help="queried word")
    parser.add_argument("language_code",
                        help="ISO 639-2 three letter language code")
    parser.add_argument(
        "--plugin-name", help="complete package name of the plugin")

    parser.set_defaults(func=__get_definition__,
                        subcommand_help=parser.print_help)

    return parser


if __name__ == "__main__":
    parser = extend_parser(None)

    args = parser.parse_args()
    if "func" in args:
        args.func(**vars(args))
    elif "subcommand_help" in args:
        args.subcommand_help()
    else:
        parser.print_help()
