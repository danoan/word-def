"""
Data models and interfaces.
"""

from enum import Enum
from importlib.metadata import version
from typing import Optional, Protocol, Sequence, TextIO

from dataclasses import dataclass


class PosTag(Enum):
    """
    Part-of-speech tags as defined in: https://universaldependencies.org/u/pos/all.html
    """

    Adjective = "Adjective"
    Adposition = "Adposition"
    Adverb = "Adverb"
    Auxiliary = "Auxiliary"
    Conjunction = "Conjunction"
    CoordinatingConjunction = "Coodrinating Conjunction"
    Determiner = "Determiner"
    Interjection = "Interjection"
    Noun = "Noun"
    Numeral = "Numeral"
    Particle = "Particle"
    Pronoun = "Pronoun"
    ProperNoun = "Proper Noun"
    Punctuation = "Punctuation"
    SubordinatingConjunction = "Subordinating Conjunction"
    Symbol = "Symbol"
    Verb = "Verb"
    Other = "Other"

    def __str__(self):
        return self.value


class PluginProtocol(Protocol):
    def get_definition(self, word: str) -> Sequence[str]:
        """
        Raises:
           UnexpectedResponseError if status code of request is different from 200.

        """
        ...

    def get_pos_tag(self, word: str) -> Sequence[PosTag]:
        """
        Get part-of-speech tag of the given word.

        The first tag correspond to the first entry in the dictionary.
        """
        ...

    def get_synonyme(self, word: str) -> Sequence[str]:
        """
        Raises:
           UnexpectedResponseError if status code of request is different from 200.

        """
        ...

    def get_usage_examples(self, word: str) -> Sequence[str]:
        """
        Raises:
           UnexpectedResponseError if status code of request is different from 200.

        """
        ...

    @staticmethod
    def version():
        """
        Get the version of the word-def package and its protocols.
        """
        return version("word-def")


class PluginFactory(Protocol):
    def get_language(self) -> str:
        """
        Get the language IETF 639-3 code.
        """
        ...

    def get_adapter(
        self, configuration_stream: Optional[TextIO] = None
    ) -> PluginProtocol:
        """
        Instantiate an implementation of PluginProtocol according with the configuration file.

        Raises:
           ConfigurationFileRequiredError if api needs configurations settings but a toml configuration file is not passed.

        """
        ...


@dataclass
class Plugin:
    package_name: str
    adapter_factory: PluginFactory
