from danoan.word_def.plugins.core import model

from dataclasses import dataclass


@dataclass
class Plugin:
    package_name: str
    adapter_factory: model.PluginFactory
