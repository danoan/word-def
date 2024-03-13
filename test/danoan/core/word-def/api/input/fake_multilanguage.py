from danoan.word_def.core import exception

from dataclasses import dataclass
from pathlib import Path
import pycountry
import toml
from typing import Sequence, Optional, TextIO


@dataclass
class Configuration:
    secret_key: str


class Adapter:
    def __init__(self, configuration: Configuration, language: str):
        self.configuration = configuration
        self.language = language

    def get_definition(self, word: str) -> Sequence[str]:
        if self.configuration.secret_key == "":
            raise exception.UnexpectedResponse(
                501, "You need authorization to request this resource."
            )
        if word == "happy" and self.language == "eng":
            json_o = {
                "word": "happy",
                "pos": "adjective",
                "definitions": [
                    "State of joy.",
                    "Someone who is happy has feelings of pleasure, usually because something nice has happened or because they feel satisfied with their life. ",
                    "A happy time, place, or relationship is full of happy feelings and pleasant experiences, or has an atmosphere in which people feel happy. "
                    "If you are happy about a situation or arrangement, you are satisfied with it, for example because you think that something is being done in the right way. ",
                ],
            }
        elif word == "joyeux" and self.language == "fra":
            json_o = {
                "word": "joyeux",
                "pos": "noun",
                "definitions": ["Qui éprouve de la joie, qui est gai."],
            }
        else:
            json_o = None

        if json_o is None:
            raise exception.UnexpectedResponse(
                404, "The word does not exist in the dictionary."
            )

        return json_o["definitions"]


class AdapterFactory:
    def version(self):
        return "0.0.1"

    def get_language(self) -> str:
        return ""

    def get_adapter(self, configuration_stream: Optional[TextIO] = None) -> Adapter:
        if configuration_stream is None:
            raise exception.ConfigurationFileRequiredError()

        configuration = Configuration(**toml.load(configuration_stream))
        return Adapter(configuration, self.get_language())
