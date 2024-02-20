from typing import List, Optional, Protocol, TextIO
from importlib.metadata import version

from dataclasses import dataclass


class PluginProtocol(Protocol):
    def get_definition(self, word: str) -> List[str]:
        ...

    def get_synonyme(self, word: str) -> List[str]:
        ...

    def get_usage_examples(self, word: str) -> List[str]:
        ...

    @staticmethod
    def version():
        return version("word-def")


class PluginFactory(Protocol):
    def get_language(self) -> str:
        ...

    def get_adapter(self, configuration_stream: Optional[TextIO] = None) -> PluginProtocol:
        ...


@dataclass
class Plugin:
    package_name: str
    adapter_factory: PluginFactory
