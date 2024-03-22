from danoan.word_def.cli.commands import (
    get_definition,
    get_pos_tag,
    get_synonym,
    get_usage_examples,
    list_dictionaries,
)

import argparse


def main():
    parser = argparse.ArgumentParser("Get word definitions and more.")
    parser.add_argument(
        "--plugin-configuration-filepath",
        help="toml file with configuration settings for word-def plugins.",
    )

    subparser_action = parser.add_subparsers()
    list_of_commands = [
        get_definition,
        get_pos_tag,
        get_synonym,
        get_usage_examples,
        list_dictionaries,
    ]
    for command in list_of_commands:
        command.extend_parser(subparser_action)

    args = parser.parse_args()
    if "func" in args:
        args.func(**vars(args))
    elif "subcommand_help" in args:
        args.subcommand_help()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
