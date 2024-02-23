from danoan.word_def.core import api, exception
from danoan.word_def.cli import utils

import argparse
from pathlib import Path
from typing import Optional


def __get_pos_tag__(
    word: str,
    language_code: str,
    plugin_configuration_filepath: Optional[Path],
    plugin_name=Optional[str],
    *args,
    **kwargs,
):
    """
    Get part-of-speech tags of a given word.
    """
    if plugin_name is None:
        plugin_name = utils.get_plugin_name(language_code)

    ss = utils.get_configuration_stream(plugin_name, plugin_configuration_filepath)

    list_of_pos_tags = []
    try:
        list_of_pos_tags = api.get_pos_tag(word, language_code, configuration_stream=ss)
    except exception.ConfigurationFileRequiredError:
        print(utils.configuration_file_required_error_message())
    except exception.PluginNotAvailableError:
        print(utils.pluging_not_available_error_message(language_code))
    except exception.PluginMethodNotImplementedError as ex:
        print(utils.plugin_method_not_implemented_error_message(ex))
    else:
        for i, pos_tag in enumerate(list_of_pos_tags, 1):
            print(f"{i}. {pos_tag}")


def extend_parser(subparser_action=None):
    command = "get-pos-tag"
    description = __get_pos_tag__.__doc__
    help = description.split(".")[0] if description else ""

    if subparser_action:
        parser = subparser_action.add_parser(
            command,
            help=help,
            description=description,
            formatter_class=argparse.RawTextHelpFormatter,
        )
    else:
        parser = argparse.ArgumentParser(
            "Get word pqrt-of-speech tags",
            description=description,
            formatter_class=argparse.RawTextHelpFormatter,
        )

    parser.add_argument("word", help="queried word")
    parser.add_argument("language_code", help="ISO 639-2 three letter language code")
    parser.add_argument("--plugin-name", help="complete package name of the plugin")

    parser.set_defaults(func=__get_pos_tag__, subcommand_help=parser.print_help)

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
