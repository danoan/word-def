from dataclasses import dataclass
from pathlib import Path
from typing import List
import toml


@dataclass
class Configuration:
    entrypoint: str
    secret_key: str


class Adapter:
    def __init__(self, configuration: Configuration):
        self.configuration = configuration

    def get_definition(self, word: str) -> List[str]:
        return ["Definition 1", "Definition 2"]


def get_language() -> str:
    pass


def get_adapater(configuration_filepath: Path) -> str:
    with open(configuration_filepath, "r") as f:
        configuration = toml.load(f)
        return Adapter(configuration)
