# How to create a word-def plugin

A `word-def` plugin is a Python package that follows the protocols
defined by `word-def`. It is how we extend the features of `word-def`,
for example, by adding support for another language.

## The `word-def` protocol

`word-def` recognizes plugins modules as plugins if they are registered under
the namespace: `danoan.word-def.plugins.modules`. All modules within
this namespace will be considered as a plugin modules by `word-def`.

A plugin module must implement a class named `AdapterFactory`, which
itself must be an implementation of the [`PluginFactory` protocol](../reference/danoan.word_def.core.model.rst#danoan.word_def.core.model.PluginFactory).

An example of implementation is given below:

```python
class AdapterFactory:
    def version(self) -> str:
        return importlib.metadata.version("my-package-name")

    def get_language(self) -> str:
        return pycountry.languages.get(name="english").alpha_3

    def get_adapter(
        self, configuration_stream: Optional[TextIO] = None
    ) -> PluginProtocol:
        if configuration_stream is None:
            raise exception.ConfigurationFileRequiredError()

        configuration = Configuration(**toml.load(configuration_stream))
        return Adapter(configuration)

```

The `get_adapter` method is responsible for instantiating a class that implements
the [`Plugin` protocol](../reference/danoan.word_def.core.model.rst#danoan.word_def.core.model.PluginProtocol).

Here's an example of such implementation:

```python
from importlib.metadata import version

class Adapter:
    def __init__(self, configuration: Configuration):
        self.configuration = configuration

    def get_definition(self, word: str) -> Sequence[str]:
        response = collins_api.get_best_matching(
            self.configuration.entrypoint,
            self.configuration.secret_key,
            collins_model.Language.English,
            word,
            collins_model.Format.JSON,
        )

        if response.status_code == 200:
            response_json = json.loads(response.text)
            html_data = response_json["entryContent"]
            html_soup = BeautifulSoup(html_data, "lxml")

            list_of_span_defs = html_soup.css.select(".def")
            list_of_definitions = list(
                map(lambda x: x.contents[0], list_of_span_defs))
            return list_of_definitions
        else:
            raise exception.UnexpectedResponse(
                response.status_code, response.text)

```

```{admonition} word-def dependency
When creating your plugin package, do not pin or specify any
range for the version of the `word-def` package. Let the package manager
resolve the `word-def` dependency, installing the appropriate version based
on the installed plugins.

Any errors regarding a plugin and `word-def` version are signaled
when the plugin is used. More information can be found at
[](../design-and-architecture.md).
```

## Plugin installation

`word-def` will try to register all modules within the namespace:
`danoan.word-def.plugins.modules`. Therefore, it is sufficient to
install the plugin as a Python package.

```bash
$ pip install word-def-plugin-myplugin
```
