from danoan.word_def.core import api, exception
from danoan.word_def.cli import utils

import argparse
from pathlib import Path
import pycountry
from types import SimpleNamespace
from typing import Optional


def __list_dictionaries__(
    language_code: Optional[str] = None,
    *args,
    **kwargs,
):
    """
    List registered dictionaries.
    """

    register = api.get_register()
    if language_code:
        languages_to_list = [language_code]
    else:
        languages_to_list = register.get_languages_available()

    for language_code in sorted(languages_to_list):
        if language_code == "":
            lang_obj = SimpleNamespace(name="Multilanguage", alpha_3="")
        else:
            lang_obj = pycountry.languages.get(alpha_3=language_code)

        print(f"{lang_obj.name.capitalize()}({lang_obj.alpha_3})")
        for plugin in register.get_language_plugins(language_code):
            print(f"{' '*4}{plugin.package_name}")


def extend_parser(subparser_action=None):
    command = "list"
    description = __list_dictionaries__.__doc__
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
            "Get word definitions",
            description=description,
            formatter_class=argparse.RawTextHelpFormatter,
        )

    parser.add_argument("--language-code", help="ISO 639-2 three letter language code")

    parser.set_defaults(func=__list_dictionaries__, subcommand_help=parser.print_help)

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
